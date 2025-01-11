"""Sources."""

from __future__ import annotations

import copy
import dataclasses
import functools
from collections.abc import Iterable, Mapping, Sequence
from typing import Final, TypeAlias

import polars as pl
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import structlog
from typing_extensions import Self

from corvic import op_graph, orm, system
from corvic.model._defaults import get_default_client, get_default_room_id
from corvic.model._proto_orm_convert import orm_to_proto
from corvic.model._resource import Resource
from corvic.model._wrapped_proto import WrappedProto
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic.table import Table
from corvic_generated.model.v1alpha import models_pb2

_logger = structlog.get_logger()

ResourceID: TypeAlias = orm.ResourceID
SourceID: TypeAlias = orm.SourceID
RoomID: TypeAlias = orm.RoomID
PipelineID: TypeAlias = orm.PipelineID


def foreign_key(
    referenced_source: SourceID | Source, *, is_excluded: bool = False
) -> op_graph.feature_type.ForeignKey:
    match referenced_source:
        case SourceID():
            return op_graph.feature_type.foreign_key(
                referenced_source, is_excluded=is_excluded
            )
        case Source():
            return op_graph.feature_type.foreign_key(
                referenced_source.id, is_excluded=is_excluded
            )


@dataclasses.dataclass(frozen=True)
class Source(WrappedProto[SourceID, models_pb2.Source]):
    """Sources describe how resources should be treated.

    Example:
    >>> Source.from_polars(order_data)
    >>>    .as_dimension_table()
    >>> )
    """

    _SOURCE_TYPE_METADATA_KEY: Final = "source_type"

    @classmethod
    def from_id(
        cls,
        source_id: SourceID,
        client: system.Client | None = None,
        session: sa_orm.Session | None = None,
    ) -> Ok[Self] | NotFoundError | InvalidArgumentError:
        client = client or get_default_client()
        return cls.load_proto_for(source_id, client, session).map(
            lambda proto_self: cls(client, proto_self)
        )

    @classmethod
    def create(
        cls,
        name: str,
        client: system.Client | None = None,
        room_id: RoomID | None = None,
    ) -> Ok[Self] | InvalidArgumentError:
        """Create a new source to be populated later."""
        client = client or get_default_client()
        room_id = room_id or get_default_room_id(client)

        proto_source = models_pb2.Source(
            name=name,
            room_id=str(room_id),
        )

        return Ok(cls(client, proto_source))

    @classmethod
    def from_resource(
        cls,
        resource: Resource,
        name: str | None = None,
        client: system.Client | None = None,
        room_id: RoomID | None = None,
    ) -> Ok[Self] | system.DataMisplacedError | InvalidArgumentError:
        return cls.from_non_tabular_resource(resource, name, client, room_id).and_then(
            lambda new_source: Table.from_parquet_file(
                new_source.client, resource.url
            ).map(lambda table: new_source.with_table(table))
        )

    @classmethod
    def from_non_tabular_resource(
        cls,
        resource: Resource,
        name: str | None = None,
        client: system.Client | None = None,
        room_id: RoomID | None = None,
    ) -> Ok[Self] | InvalidArgumentError:
        """Construct a source for a resource that requires some preprocessing.

        This flavor populates all of the metadata that comes from the resource
        but does not populate table. Callers are expected to populate table later.
        """
        client = client or resource.client
        room_id = room_id or resource.room_id

        proto_source = models_pb2.Source(
            name=name or resource.name,
            resource_id=str(resource.id),
            room_id=str(room_id),
        )

        return Ok(cls(client, proto_source))

    @classmethod
    def from_polars(
        cls,
        name: str,
        data_frame: pl.DataFrame,
        client: system.Client | None = None,
        room_id: RoomID | None = None,
    ) -> Self:
        """Create a source from a pl.DataFrame.

        Args:
            name: a unique name for this source
            data_frame: a polars DataFrame
            client: use a particular system.Client instead of the default
            room_id: room to associate this source with. Use the default room if None.
        """
        client = client or get_default_client()
        resource = Resource.from_polars(data_frame, client).commit().unwrap_or_raise()
        return cls.from_resource(
            resource, name=name, client=client, room_id=room_id
        ).unwrap_or_raise()

    def with_table(self, table: Table) -> Self:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.table_op_graph.CopyFrom(table.op_graph.to_proto())
        return dataclasses.replace(
            self,
            proto_self=proto_self,
        )

    @staticmethod
    def _to_orm_if_exists(
        id_val: RoomID, client: system.Client
    ) -> Ok[RoomID] | NotFoundError:
        match id_val:
            case RoomID():
                orm_class = orm.Room

        with orm.Session(client.sa_engine) as session:
            if session.get(orm_class, id_val) is not None:
                return Ok(id_val)
        return NotFoundError("entity not found")

    @classmethod
    def _generate_sources(
        cls, query: sa.Select[tuple[orm.Source]], client: system.Client
    ):
        with orm.Session(client.sa_engine) as session:
            it = iter(session.scalars(query))
            while True:
                try:
                    for val in it:
                        yield cls(
                            client,
                            orm_to_proto(val),
                        )
                except Exception:  # noqa: PERF203
                    _logger.exception(
                        "omitting source from list: "
                        + "failed to parse source from database entry",
                    )
                else:
                    break

    @classmethod
    def list(
        cls,
        room_id: RoomID | None = None,
        resource_id: ResourceID | None = None,
        client: system.Client | None = None,
    ) -> Ok[Iterable[Source]] | NotFoundError:
        """List sources that exist in storage."""
        client = client or get_default_client()
        query = sa.select(orm.Source)
        if room_id is not None:
            match cls._to_orm_if_exists(room_id, client):
                case NotFoundError():
                    return NotFoundError("room not found", room_id=room_id)
                case Ok(orm_id):
                    query = query.filter_by(room_id=orm_id)

        if resource_id is not None:
            match Resource.from_id(resource_id, client):
                case NotFoundError() | InvalidArgumentError():
                    return NotFoundError("resource not found", resource_id=resource_id)
                case Ok(resource):
                    query = query.filter(
                        orm.Source.resource_associations.any(resource_id=resource.id)
                        | orm.Source.pipeline_output_refs.any(
                            pipeline_id=resource.pipeline_id
                        )
                    )
        query = query.order_by(sa.desc(orm.Source.created_at))

        return Ok(list(cls._generate_sources(query, client)))

    def with_feature_types(
        self, feature_types: Mapping[str, op_graph.FeatureType]
    ) -> Self:
        """Assign a Feature Type to each column in source.

        Args:
            feature_types: Mapping between column name and feature type

        Example:
        >>> with_feature_types(
        >>>        {
        >>>            "id": corvic.model.feature_type.primary_key(),
        >>>            "customer_id": corvic.model.feature_type.foreign_key(
        >>>                customer_source.id
        >>>            ),
        >>>        },
        >>>    )
        """
        return self.with_table(self.table.update_feature_types(feature_types))

    @functools.cached_property
    def table(self):
        return Table.from_ops(
            self.client, op_graph.op.from_proto(self.proto_self.table_op_graph)
        )

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def room_id(self) -> RoomID:
        return RoomID(self.proto_self.room_id)

    @property
    def pipeline_id(self) -> PipelineID | None:
        return PipelineID(self.proto_self.pipeline_id) or None

    @property
    def resource_ids(self) -> Sequence[ResourceID]:
        return [ResourceID(self.proto_self.resource_id)]
