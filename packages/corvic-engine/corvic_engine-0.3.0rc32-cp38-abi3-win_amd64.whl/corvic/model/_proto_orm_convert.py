import dataclasses
from collections.abc import Sequence
from typing import Generic, TypeVar

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from google.protobuf import timestamp_pb2
from more_itertools import flatten
from typing_extensions import overload

from corvic import orm
from corvic.result import InvalidArgumentError, Ok
from corvic_generated.model.v1alpha import models_pb2

UNCOMMITTED_ID_PREFIX = "__uncommitted_object-"

_Proto = (
    models_pb2.Resource
    | models_pb2.Source
    | models_pb2.FeatureView
    | models_pb2.Space
    | models_pb2.FeatureViewSource
    | models_pb2.Agent
    | models_pb2.Pipeline
)
_Orm = (
    orm.Resource
    | orm.Source
    | orm.FeatureView
    | orm.Space
    | orm.FeatureViewSource
    | orm.Agent
    | orm.Pipeline
)
_ID = TypeVar(
    "_ID",
    orm.ResourceID,
    orm.SourceID,
    orm.FeatureViewID,
    orm.SpaceID,
    orm.FeatureViewSourceID,
    orm.AgentID,
    orm.PipelineID,
)
OrmID = (
    orm.ResourceID
    | orm.SourceID
    | orm.FeatureViewID
    | orm.SpaceID
    | orm.FeatureViewSourceID
    | orm.AgentID
    | orm.PipelineID
)


@overload
def id_class_for(val: models_pb2.Resource) -> type[orm.ResourceID]: ...


@overload
def id_class_for(val: models_pb2.Source) -> type[orm.SourceID]: ...


@overload
def id_class_for(val: models_pb2.FeatureView) -> type[orm.FeatureViewID]: ...


@overload
def id_class_for(val: models_pb2.Space) -> type[orm.SpaceID]: ...


@overload
def id_class_for(
    val: models_pb2.FeatureViewSource,
) -> type[orm.FeatureViewSourceID]: ...


@overload
def id_class_for(val: models_pb2.Agent) -> type[orm.AgentID]: ...


@overload
def id_class_for(val: models_pb2.Pipeline) -> type[orm.PipelineID]: ...


def id_class_for(val: _Proto) -> type[OrmID]:
    match val:
        case models_pb2.Resource():
            return orm.ResourceID
        case models_pb2.Source():
            return orm.SourceID
        case models_pb2.FeatureView():
            return orm.FeatureViewID
        case models_pb2.Space():
            return orm.SpaceID
        case models_pb2.FeatureViewSource():
            return orm.FeatureViewSourceID
        case models_pb2.Agent():
            return orm.AgentID
        case models_pb2.Pipeline():
            return orm.PipelineID


@overload
def orm_class_for(val: orm.ResourceID) -> type[orm.Resource]: ...


@overload
def orm_class_for(val: orm.SourceID) -> type[orm.Source]: ...


@overload
def orm_class_for(val: orm.FeatureViewID) -> type[orm.FeatureView]: ...


@overload
def orm_class_for(val: orm.SpaceID) -> type[orm.Space]: ...


@overload
def orm_class_for(val: orm.FeatureViewSourceID) -> type[orm.FeatureViewSource]: ...


@overload
def orm_class_for(val: orm.AgentID) -> type[orm.Agent]: ...


@overload
def orm_class_for(val: orm.PipelineID) -> type[orm.Pipeline]: ...


@overload
def orm_class_for(val: models_pb2.Resource) -> type[orm.Resource]: ...


@overload
def orm_class_for(val: models_pb2.Source) -> type[orm.Source]: ...


@overload
def orm_class_for(val: models_pb2.FeatureView) -> type[orm.FeatureView]: ...


@overload
def orm_class_for(val: models_pb2.Space) -> type[orm.Space]: ...


@overload
def orm_class_for(val: models_pb2.FeatureViewSource) -> type[orm.FeatureViewSource]: ...


@overload
def orm_class_for(val: models_pb2.Agent) -> type[orm.Agent]: ...


@overload
def orm_class_for(val: models_pb2.Pipeline) -> type[orm.Pipeline]: ...


def orm_class_for(val: OrmID | _Proto) -> type[_Orm]:
    if isinstance(val, _Proto):
        id_val: OrmID = id_class_for(val)()
    else:
        id_val = val
    match id_val:
        case orm.ResourceID():
            return orm.Resource
        case orm.SourceID():
            return orm.Source
        case orm.FeatureViewID():
            return orm.FeatureView
        case orm.SpaceID():
            return orm.Space
        case orm.FeatureViewSourceID():
            return orm.FeatureViewSource
        case orm.AgentID():
            return orm.Agent
        case orm.PipelineID():
            return orm.Pipeline


@dataclasses.dataclass
class _OrmIDs(Generic[_ID]):
    obj_id: _ID | None
    room_id: orm.RoomID | None


def _translate_orm_ids(
    proto_obj: _Proto, obj_id_class: type[_ID]
) -> Ok[_OrmIDs[_ID]] | orm.InvalidORMIdentifierError:
    if proto_obj.id.startswith(UNCOMMITTED_ID_PREFIX):
        obj_id = None
    else:
        obj_id = obj_id_class(proto_obj.id)
        match obj_id.to_db():
            case orm.InvalidORMIdentifierError() as err:
                return err
            case Ok():
                pass

    match proto_obj:
        case (
            models_pb2.Resource()
            | models_pb2.Source()
            | models_pb2.FeatureView()
            | models_pb2.Space()
            | models_pb2.Agent()
            | models_pb2.Pipeline()
        ):
            room_id = orm.RoomID(proto_obj.room_id)
            match room_id.to_db():
                case orm.InvalidORMIdentifierError() as err:
                    return err
                case Ok():
                    pass
        case models_pb2.FeatureViewSource():
            room_id = None

    return Ok(_OrmIDs(obj_id, room_id))


@overload
def orm_to_proto(orm_obj: orm.Resource) -> models_pb2.Resource: ...


@overload
def orm_to_proto(orm_obj: orm.Source) -> models_pb2.Source: ...


@overload
def orm_to_proto(orm_obj: orm.FeatureView) -> models_pb2.FeatureView: ...


@overload
def orm_to_proto(orm_obj: orm.Space) -> models_pb2.Space: ...


@overload
def orm_to_proto(orm_obj: orm.FeatureViewSource) -> models_pb2.FeatureViewSource: ...


@overload
def orm_to_proto(orm_obj: orm.Agent) -> models_pb2.Agent: ...


@overload
def orm_to_proto(orm_obj: orm.Pipeline) -> models_pb2.Pipeline: ...


def orm_to_proto(orm_obj: _Orm) -> _Proto:
    if orm_obj.created_at is not None:
        created_at = timestamp_pb2.Timestamp()
        created_at.FromDatetime(orm_obj.created_at)
    else:
        created_at = None
    match orm_obj:
        case orm.Resource():
            return models_pb2.Resource(
                id=str(orm_obj.id),
                name=orm_obj.name,
                description=orm_obj.description,
                mime_type=orm_obj.mime_type,
                url=orm_obj.url,
                md5=orm_obj.md5,
                size=orm_obj.size,
                original_path=orm_obj.original_path,
                room_id=str(orm_obj.room_id),
                source_ids=[str(val.source_id) for val in orm_obj.source_associations],
                org_id=str(orm_obj.org_id),
                pipeline_id=str(orm_obj.pipeline_input_refs[-1].pipeline.id)
                if orm_obj.pipeline_input_refs
                else None,
                created_at=created_at,
            )
        case orm.Source():
            return models_pb2.Source(
                id=str(orm_obj.id),
                name=orm_obj.name,
                table_op_graph=orm_obj.table_op_graph,
                room_id=str(orm_obj.room_id),
                resource_id=str(orm_obj.resource_associations[0].resource_id)
                if orm_obj.resource_associations
                else "",
                org_id=str(orm_obj.org_id),
                pipeline_id=str(orm_obj.pipeline_output_refs[-1].pipeline.id)
                if orm_obj.pipeline_output_refs
                else None,
                created_at=created_at,
            )
        case orm.Pipeline():
            return models_pb2.Pipeline(
                id=str(orm_obj.id),
                name=orm_obj.name,
                room_id=str(orm_obj.room_id),
                resource_inputs={
                    input_obj.name: orm_to_proto(input_obj.resource)
                    for input_obj in orm_obj.inputs
                },
                source_outputs={
                    output_obj.name: orm_to_proto(output_obj.source)
                    for output_obj in orm_obj.outputs
                },
                pipeline_transformation=orm_obj.transformation,
                org_id=str(orm_obj.org_id),
                created_at=created_at,
                description=orm_obj.description,
            )
        case orm.FeatureView():
            return models_pb2.FeatureView(
                id=str(orm_obj.id),
                name=orm_obj.name,
                description=orm_obj.description,
                room_id=str(orm_obj.room_id),
                feature_view_output=orm_obj.feature_view_output,
                feature_view_sources=[
                    orm_to_proto(fvs) for fvs in orm_obj.feature_view_sources
                ],
                org_id=str(orm_obj.org_id),
                created_at=created_at,
            )
        case orm.Space():
            raise NotImplementedError()
        case orm.FeatureViewSource():
            return models_pb2.FeatureViewSource(
                id=str(orm_obj.id),
                source=orm_to_proto(orm_obj.source),
                table_op_graph=orm_obj.table_op_graph,
                drop_disconnected=orm_obj.drop_disconnected,
                org_id=str(orm_obj.org_id),
                created_at=created_at,
            )
        case orm.Agent():
            return models_pb2.Agent(
                id=str(orm_obj.id),
                name=orm_obj.name,
                room_id=str(orm_obj.room_id),
                agent_parameters=orm_obj.parameters,
                org_id=str(orm_obj.org_id),
                created_at=created_at,
            )


@overload
def proto_to_orm(
    proto_obj: models_pb2.Resource, session: sa_orm.Session
) -> Ok[orm.Resource] | orm.InvalidORMIdentifierError: ...


@overload
def proto_to_orm(
    proto_obj: models_pb2.Source, session: sa_orm.Session
) -> Ok[orm.Source] | orm.InvalidORMIdentifierError: ...


@overload
def proto_to_orm(
    proto_obj: models_pb2.Pipeline, session: sa_orm.Session
) -> Ok[orm.Pipeline] | orm.InvalidORMIdentifierError: ...


@overload
def proto_to_orm(
    proto_obj: models_pb2.FeatureView, session: sa_orm.Session
) -> Ok[orm.FeatureView] | orm.InvalidORMIdentifierError: ...


@overload
def proto_to_orm(
    proto_obj: models_pb2.Space, session: sa_orm.Session
) -> Ok[orm.Space] | orm.InvalidORMIdentifierError: ...


@overload
def proto_to_orm(
    proto_obj: models_pb2.FeatureViewSource, session: sa_orm.Session
) -> Ok[orm.FeatureViewSource] | orm.InvalidORMIdentifierError: ...


@overload
def proto_to_orm(
    proto_obj: models_pb2.Agent, session: sa_orm.Session
) -> Ok[orm.Agent] | orm.InvalidORMIdentifierError: ...


def _resource_proto_to_orm(
    proto_obj: models_pb2.Resource, session: sa_orm.Session
) -> Ok[orm.Resource] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.ResourceID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")

    source_ids = list[orm.SourceID]()
    for source_id in proto_obj.source_ids:
        orm_id = orm.SourceID(source_id)
        match orm_id.to_db():
            case orm.InvalidORMIdentifierError() as err:
                return err
            case Ok():
                source_ids.append(orm_id)
    orm_obj = orm.Resource(
        id=ids.obj_id,
        name=proto_obj.name,
        description=proto_obj.description,
        mime_type=proto_obj.mime_type,
        md5=proto_obj.md5,
        url=proto_obj.url,
        size=proto_obj.size,
        original_path=proto_obj.original_path,
        room_id=ids.room_id,
        source_associations=[
            orm.SourceResourceAssociation(source_id=src_id, resource_id=ids.obj_id)
            for src_id in source_ids
        ],
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)
        for assn in orm_obj.source_associations:
            assn.org_id = orm_obj.org_id

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    return Ok(orm_obj)


def _pipeline_proto_to_orm(  # noqa: C901
    proto_obj: models_pb2.Pipeline, session: sa_orm.Session
) -> Ok[orm.Pipeline] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.PipelineID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit pipeline")

    orm_obj = orm.Pipeline(
        id=ids.obj_id,
        name=proto_obj.name,
        room_id=ids.room_id,
        transformation=proto_obj.pipeline_transformation,
        description=proto_obj.description,
    )

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    for name, val in proto_obj.resource_inputs.items():
        if any(input.name == name for input in orm_obj.inputs):
            continue
        match _resource_proto_to_orm(val, session):
            case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
                return err
            case Ok(resource_orm):
                if resource_orm.id:
                    resource_orm = session.merge(resource_orm)
                else:
                    session.add(resource_orm)
                session.merge(
                    orm.PipelineInput(
                        pipeline=orm_obj, resource=resource_orm, name=name
                    )
                )

    for name, val in proto_obj.source_outputs.items():
        if any(output.name == name for output in orm_obj.outputs):
            continue
        match _source_proto_to_orm(val, session):
            case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
                return err
            case Ok(source_orm):
                if source_orm.id:
                    source_orm = session.merge(source_orm)
                else:
                    session.add(source_orm)
                session.merge(
                    orm.PipelineOutput(pipeline=orm_obj, source=source_orm, name=name)
                )
    if proto_obj.org_id:
        org_id = orm.OrgID(proto_obj.org_id)
        orm_obj.org_id = org_id
        for obj in flatten((orm_obj.inputs, orm_obj.outputs)):
            obj.org_id = orm.OrgID(proto_obj.org_id)
    return Ok(orm_obj)


def _source_proto_to_orm(
    proto_obj: models_pb2.Source, session: sa_orm.Session
) -> Ok[orm.Source] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.SourceID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")
    resource_id = orm.ResourceID(proto_obj.resource_id)
    if resource_id:
        associations = [
            orm.SourceResourceAssociation(source_id=ids.obj_id, resource_id=resource_id)
        ]
    else:
        associations = list[orm.SourceResourceAssociation]()

    orm_obj = orm.Source(
        id=ids.obj_id,
        name=proto_obj.name,
        table_op_graph=proto_obj.table_op_graph,
        room_id=ids.room_id,
        resource_associations=associations,
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)
        for assn in orm_obj.resource_associations:
            assn.org_id = orm.OrgID(proto_obj.org_id)
    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    return Ok(orm_obj)


def _agent_proto_to_orm(
    proto_obj: models_pb2.Agent, session: sa_orm.Session
) -> Ok[orm.Agent] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.AgentID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")

    orm_obj = orm.Agent(
        id=ids.obj_id,
        name=proto_obj.name,
        parameters=proto_obj.agent_parameters,
        room_id=ids.room_id,
    )

    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)
    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    return Ok(orm_obj)


def _feature_view_proto_to_orm(
    proto_obj: models_pb2.FeatureView, session: sa_orm.Session
) -> Ok[orm.FeatureView] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.FeatureViewID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")

    feature_view_sources = list[orm.FeatureViewSource]()
    for fvs in proto_obj.feature_view_sources:
        match proto_to_orm(fvs, session):
            case orm.InvalidORMIdentifierError() as err:
                return err
            case Ok(orm_fvs):
                if orm_fvs.id:
                    orm_fvs = session.merge(orm_fvs)
                else:
                    session.add(orm_fvs)
                feature_view_sources.append(orm_fvs)

    orm_obj = orm.FeatureView(
        id=ids.obj_id,
        name=proto_obj.name,
        description=proto_obj.description,
        room_id=ids.room_id,
        feature_view_output=proto_obj.feature_view_output,
        feature_view_sources=feature_view_sources,
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)
    return Ok(orm_obj)


def _feature_view_source_proto_to_orm(
    proto_obj: models_pb2.FeatureViewSource, session: sa_orm.Session
) -> Ok[orm.FeatureViewSource] | orm.InvalidORMIdentifierError:
    match proto_to_orm(proto_obj.source, session):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(source):
            pass

    if source.id:
        source = session.merge(source)
    else:
        session.add(source)
    orm_obj = orm.FeatureViewSource(
        table_op_graph=proto_obj.table_op_graph,
        drop_disconnected=proto_obj.drop_disconnected,
        source=source,
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)
    return Ok(orm_obj)


def proto_to_orm(
    proto_obj: _Proto, session: sa_orm.Session
) -> Ok[_Orm] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match proto_obj:
        case models_pb2.Resource():
            return _resource_proto_to_orm(proto_obj, session)
        case models_pb2.Source():
            return _source_proto_to_orm(proto_obj, session)
        case models_pb2.FeatureView():
            return _feature_view_proto_to_orm(proto_obj, session)
        case models_pb2.Space():
            raise NotImplementedError()
        case models_pb2.FeatureViewSource():
            return _feature_view_source_proto_to_orm(proto_obj, session)
        case models_pb2.Agent():
            return _agent_proto_to_orm(proto_obj, session)
        case models_pb2.Pipeline():
            return _pipeline_proto_to_orm(proto_obj, session)


def _delete_sources(
    orm_ids: Sequence[orm.SourceID], session: sa_orm.Session
) -> Ok[None] | InvalidArgumentError:
    feat_view_refs = list(
        session.scalars(
            sa.select(orm.FeatureViewSource)
            .where(orm.FeatureViewSource.source_id.in_(orm_ids))
            .limit(1)
        )
    )

    if feat_view_refs:
        return InvalidArgumentError(
            "cannot delete a source that still has feature views"
        )
    session.execute(sa.delete(orm.Source).where(orm.Source.id.in_(orm_ids)))
    return Ok(None)


def _delete_pipeline(
    orm_id: orm.PipelineID, session: sa_orm.Session
) -> Ok[None] | InvalidArgumentError:
    source_ids = [
        val[0]
        for val in session.execute(
            sa.select(orm.Source.id).where(
                orm.Source.id.in_(
                    sa.select(orm.PipelineOutput.source_id)
                    .join(orm.Pipeline)
                    .where(orm.Pipeline.id == orm_id)
                )
            )
        )
        if val[0] is not None
    ]
    match _delete_sources(source_ids, session):
        case InvalidArgumentError() as err:
            return err
        case Ok():
            pass

    session.execute(
        sa.delete(orm.Resource).where(
            orm.Resource.id.in_(
                sa.select(orm.PipelineInput.resource_id)
                .join(orm.Pipeline)
                .where(orm.Pipeline.id == orm_id)
            )
        )
    )
    session.execute(sa.delete(orm.Pipeline).where(orm.Pipeline.id == orm_id))
    return Ok(None)


def delete_orm_obj(
    orm_id: _ID, session: sa_orm.Session
) -> Ok[None] | InvalidArgumentError:
    match orm_id:
        case orm.ResourceID():
            return Ok(None)
        case orm.SourceID():
            return _delete_sources([orm_id], session)
        case orm.FeatureViewID():
            session.execute(
                sa.delete(orm.FeatureView).where(orm.FeatureView.id == orm_id)
            )
            return Ok(None)
        case orm.SpaceID():
            session.execute(sa.delete(orm.Space).where(orm.Space.id == orm_id))
            return Ok(None)
        case orm.FeatureViewSourceID():
            session.execute(
                sa.delete(orm.FeatureViewSource).where(
                    orm.FeatureViewSource.id == orm_id
                )
            )
            return Ok(None)
        case orm.AgentID():
            session.execute(sa.delete(orm.Agent).where(orm.Agent.id == orm_id))
            return Ok(None)
        case orm.PipelineID():
            return _delete_pipeline(orm_id, session)
