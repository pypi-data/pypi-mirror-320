"""Common model base."""

import abc
import contextlib
import copy
import dataclasses
import datetime
import functools
import uuid
from collections.abc import Callable, Iterator
from typing import Generic, TypeVar, cast

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import structlog
from typing_extensions import Self

from corvic import orm, system
from corvic.model._proto_orm_convert import (
    UNCOMMITTED_ID_PREFIX,
    delete_orm_obj,
    id_class_for,
    orm_class_for,
    orm_to_proto,
    proto_to_orm,
)
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic_generated.model.v1alpha import models_pb2

_OrmObj = TypeVar(
    "_OrmObj",
    orm.Agent,
    orm.FeatureView,
    orm.FeatureViewSource,
    orm.Pipeline,
    orm.Resource,
    orm.Source,
    orm.Space,
)
_ID = TypeVar(
    "_ID",
    orm.AgentID,
    orm.FeatureViewID,
    orm.FeatureViewSourceID,
    orm.PipelineID,
    orm.ResourceID,
    orm.SourceID,
    orm.SpaceID,
)
_ProtoObj = TypeVar(
    "_ProtoObj",
    models_pb2.Agent,
    models_pb2.FeatureView,
    models_pb2.FeatureViewSource,
    models_pb2.Pipeline,
    models_pb2.Resource,
    models_pb2.Source,
    models_pb2.Space,
)

_logger = structlog.get_logger()

_T = TypeVar("_T")


def _generate_uncommitted_id_str():
    return f"{UNCOMMITTED_ID_PREFIX}{uuid.uuid4()}"


@contextlib.contextmanager
def _create_or_join_session(
    client: system.Client, existing_session: sa_orm.Session | None
) -> Iterator[sa_orm.Session]:
    if existing_session:
        yield existing_session
    else:
        with sa_orm.Session(client.sa_engine) as session:
            yield session


@dataclasses.dataclass(frozen=True)
class WrappedProto(Generic[_ID, _ProtoObj], abc.ABC):
    """Base for orm wrappers providing a unified update mechanism."""

    client: system.Client
    proto_self: _ProtoObj

    def __post_init__(self):
        if not self.proto_self.id:
            self.proto_self.id = _generate_uncommitted_id_str()

    @functools.cached_property
    def id(self) -> _ID:
        return cast(_ID, id_class_for(self.proto_self).from_str(self.proto_self.id))

    @property
    def created_at(self) -> datetime.datetime | None:
        if self.proto_self.created_at:
            return self.proto_self.created_at.ToDatetime(tzinfo=datetime.timezone.utc)
        return None

    @classmethod
    def load_proto_for(
        cls,
        obj_id: _ID,
        client: system.Client,
        existing_session: sa_orm.Session | None = None,
    ) -> Ok[_ProtoObj] | NotFoundError | InvalidArgumentError:
        """Create a model object by loading it from the database."""
        with _create_or_join_session(client, existing_session) as session:
            orm_self = session.get(orm_class_for(obj_id), obj_id)
            if orm_self is None:
                return NotFoundError("object with given id does not exists", id=obj_id)
            proto_self = cast(_ProtoObj, orm_to_proto(orm_self))
        return Ok(proto_self)

    @classmethod
    def _generate_query_results(
        cls, query: sa.Select[tuple[_T]], session: sa_orm.Session
    ) -> Iterator[_T]:
        it = iter(session.scalars(query))
        while True:
            try:
                yield from it
            except Exception:  # noqa: PERF203
                _logger.exception(
                    "omitting source from list: "
                    + "failed to parse source from database entry",
                )
            else:
                break

    @classmethod
    def list_as_proto(
        cls,
        orm_class: type[_OrmObj],
        client: system.Client,
        limit: int | None = None,
        room_id: orm.RoomID | None = None,
        created_before: datetime.datetime | None = None,
        additional_query_transform: Callable[
            [sa.Select[tuple[_OrmObj]]], sa.Select[tuple[_OrmObj]]
        ]
        | None = None,
    ) -> Ok[list[_ProtoObj]] | NotFoundError | InvalidArgumentError:
        """List sources that exist in storage."""
        query = sa.select(orm_class).order_by(sa.desc(orm_class.created_at))
        if limit is not None:
            if limit < 0:
                return InvalidArgumentError("limit cannot be negative")
            query = query.limit(limit)
        with sa_orm.Session(client.sa_engine) as session:
            if room_id:
                if session.get(orm.Room, room_id) is None:
                    return NotFoundError("room not found", room_id=room_id)
                query = query.filter_by(room_id=room_id)
            if created_before:
                query = query.filter(orm_class.created_at < created_before)
            if additional_query_transform:
                query = additional_query_transform(query)
            return Ok(
                [
                    cast(_ProtoObj, orm_to_proto(val))
                    for val in cls._generate_query_results(query, session)
                ]
            )

    def commit(self) -> Ok[Self] | InvalidArgumentError:
        """Store this object in the database at its id or a newly allocated id.

        This overwrites the entry at id in the database so that future readers will see
        this object. One of `id` or `derived_from_id` cannot be empty or None.
        """
        with orm.Session(self.client.sa_engine) as session:
            try:
                new_orm_self = proto_to_orm(self.proto_self, session).unwrap_or_raise()
                session.commit()
            except sa.exc.DatabaseError as err:
                return InvalidArgumentError.from_(err)
            return Ok(
                dataclasses.replace(
                    self,
                    proto_self=orm_to_proto(new_orm_self),
                )
            )

    def add_to_session(self, session: orm.Session) -> Ok[None] | InvalidArgumentError:
        """Like commit, but just calls session.flush to check for database errors.

        This adds the updated object to a transaction in session. Unlike commit
        this will not return the updated object because some values may not be known
        until the wrapped transaction commits.
        """
        try:
            _ = proto_to_orm(self.proto_self, session).unwrap_or_raise()
            session.flush()
        except sa.exc.DatabaseError as err:
            return InvalidArgumentError.from_(err)
        return Ok(None)

    def delete(self) -> Ok[Self] | NotFoundError | InvalidArgumentError:
        with sa_orm.Session(
            self.client.sa_engine, expire_on_commit=False, autoflush=False
        ) as session:
            match delete_orm_obj(self.id, session):
                case InvalidArgumentError() as err:
                    return err
                case Ok(None):
                    pass
            session.commit()

            new_proto_self = copy.copy(self.proto_self)
            new_proto_self.id = ""

            return Ok(
                dataclasses.replace(
                    self,
                    proto_self=new_proto_self,
                )
            )
