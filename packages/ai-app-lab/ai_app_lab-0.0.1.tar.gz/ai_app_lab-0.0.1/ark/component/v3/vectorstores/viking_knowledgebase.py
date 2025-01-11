import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union, get_args

import pydantic
from deprecated import deprecated
from pydantic import BaseModel, field_validator, model_validator
from volcengine.viking_knowledgebase import (
    Collection,
    EmbddingModelType,
    Field,
    FieldType,
    IndexType,
    Point,
    VikingKnowledgeBaseService,
)

from ark.core.client import get_client_pool
from ark.core.rag import KnowledgeBase, KnowledgeChunk, KnowledgeDoc, KnowledgeSchema
from ark.core.utils.errorsv3 import (
    InvalidParameter,
    KnowledgeBaseError,
    MissingParameter,
)

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)

INSTANCE_TYPE = {
    "int64": int,
    "float32": float,
    "string": str,
    "bool": bool,
}

LIST_TYPE = {
    "list<string>": List[str],
    "list<int64>": List[int],
}

FIELD_ENUM_MAP = {
    "int64": FieldType.Int64,
    "string": FieldType.String,
    "bool": FieldType.Bool,
    "list<string>": FieldType.List_String,
    "list<int64>": FieldType.List_Int64,
}

ALLOWED_KEYS = {
    "chunking_strategy",
    "chunking_identifier",
    "chunk_length",
    "merge_small_chunks",
}


def _init_service(
    ak: str = "", sk: str = "", **kwargs: Any
) -> VikingKnowledgeBaseService:
    return VikingKnowledgeBaseService(
        ak=ak or os.getenv("VOLC_ACCESSKEY"), sk=sk or os.getenv("VOLC_SECRETKEY")
    )


def _default_fields_to_dict(field: Field) -> Dict[str, Any]:
    return {
        "field_name": field.field_name,
        "field_type": field.field_type,
        "default_val": field.field_val,
    }


def _is_field_type_matched(obj: Any, expected_type: str) -> bool:
    field_type = INSTANCE_TYPE.get(expected_type)
    if field_type:
        return isinstance(obj, field_type)
    list_type = LIST_TYPE.get(expected_type)
    item_type = get_args(list_type)
    return isinstance(list_type, list) and all(
        isinstance(item, item_type) for item in list_type
    )


def _is_valid_field_type(field_type: str) -> bool:
    for field in FieldType:
        if field_type == field.value:
            return True
    return False


def _merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in merged_dict:
            if isinstance(value, dict) and isinstance(merged_dict[key], dict):
                merged_dict[key] = _merge_dicts(merged_dict[key], value)
            elif isinstance(value, list) and isinstance(merged_dict[key], list):
                merged_dict[key].extend(value)
            else:
                merged_dict[key] = value
        else:
            merged_dict[key] = value
    return merged_dict


def _merge_scalars(
    scalars_collection: List[Dict[str, Any]],
    scalars_user: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    if scalars_user is not None:
        scalars = scalars_user
    else:
        return scalars_collection

    key = "field_name"
    seen = set()

    for _dic in scalars_collection:
        if _dic[key] not in seen:
            scalars.append(
                {
                    "field_name": _dic["field_name"],
                    "field_type": _dic["field_type"],
                    "field_value": _dic["default_val"],
                }
            )
            seen.add(_dic[key])
    return scalars


class PrimaryKey(BaseModel):
    name: str
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, field_type: str) -> str:
        assert _is_valid_field_type(field_type), InvalidParameter(
            f"field type {field_type} not in supported field types"
        )
        return field_type


class Vector(BaseModel):
    name: str
    model: str
    type: str
    embedding_type: Optional[str] = pydantic.Field(default="llm")
    dim: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def validate_vector(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        field_type, dim, model, embedding_type = (
            v.get("type"),
            v.get("dim"),
            v.get("model"),
            v.get("embedding_type", "llm"),
        )

        assert field_type, MissingParameter("type")
        assert model, MissingParameter("model")
        assert embedding_type in ("vdb", "llm"), InvalidParameter("embedding_type")
        assert _is_valid_field_type(field_type), InvalidParameter(
            f"field type {field_type} not in supported field types"
        )

        if dim:
            assert 4 <= dim <= 2048, InvalidParameter("dim should be in range [4,2048]")
            assert dim % 4 == 0, InvalidParameter("dim should be dived by 4")

        return v


class Scalar(BaseModel):
    field_name: str
    field_type: str
    default_val: Optional[Any] = None

    @model_validator(mode="before")
    @classmethod
    def validate_scalar(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        field_type, default_val = v.get("field_type"), v.get("default_val")
        assert field_type, MissingParameter("field_type")
        assert _is_valid_field_type(field_type), InvalidParameter(
            f"field type {field_type} not in supported field types"
        )

        if default_val:
            assert _is_field_type_matched(default_val, field_type), InvalidParameter(
                "default_val"
            )
        return v


class VikingKnowledgeBaseSchema(KnowledgeSchema):
    @field_validator("primary_key")
    @classmethod
    def validate_primary_key(cls, v: Dict[str, str]) -> Dict[str, str]:
        try:
            PrimaryKey.model_validate(v)
            return v
        except Exception as e:
            raise e

    @field_validator("vector")
    @classmethod
    def validate_vector(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        try:
            Vector.model_validate(v)
            return v
        except Exception as e:
            raise e

    @field_validator("scalars")
    @classmethod
    def validate_scalars(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            for scalar in v:
                Scalar.model_validate(scalar)

            return v
        except Exception as e:
            raise e

    def schema_to_field(self, data: Dict[str, Any]) -> Field:
        field_name = data.get("name")
        return Field(
            field_name=field_name,
            field_type=FIELD_ENUM_MAP.get(data.get("type", "")),
            default_val=data.get("default_val"),
            dim=data.get("dim"),
            is_primary_key=(field_name == self.primary_key.get("name")),
            pipeline_name=data.get("model")
            if data.get("embedding_type", "llm") == "vdb"
            else None,
        )

    @property
    def fields(self) -> List[Field]:
        fields: List[Field] = []
        fields.append(self.schema_to_field(self.primary_key))
        fields.append(self.schema_to_field(self.vector))

        for scalar in self.scalars:
            fields.append(self.schema_to_field(scalar))

        return fields

    def get_primary_key_data(self, field: Dict[str, Any]) -> Tuple[str, Any]:
        key_name, key_type = (
            self.primary_key.get("name"),
            self.primary_key.get("type"),
        )

        assert key_name, MissingParameter("name")
        assert key_type, MissingParameter("type")

        primary_key = field.get(key_name)
        assert primary_key, "primary key should not be empty"
        assert _is_field_type_matched(primary_key, key_type), InvalidParameter(
            f"primary_key should be type {key_type}"
        )

        return key_name, primary_key

    def get_vector_data(
        self, field: Dict[str, Any]
    ) -> Tuple[str, Union[List[Any], str]]:
        vector_name, vector_type, embedding_type = (
            self.vector.get("name"),
            self.vector.get("type"),
            self.vector.get("embedding_type"),
        )
        assert vector_name, MissingParameter("vector name")
        assert vector_type, MissingParameter("vector type")

        if embedding_type == "vdb":
            vector = field.get(vector_name, "")
            assert _is_field_type_matched(vector, vector_type), InvalidParameter(
                f"vector should be type {vector_type}"
            )

            return vector_name, vector
        # embedding_type == "llm", viking search do not provide vector field
        return vector_name, ""

    def get_scalar_data(self, field: Dict[str, Any]) -> Dict[str, Any]:
        scalar_dic: Dict[str, Any] = {}
        for scalar_schema in self.scalars:
            scalar_name, scalar_type, default_val = (
                scalar_schema.get("name"),
                scalar_schema.get("type"),
                scalar_schema.get("default_val"),
            )
            assert scalar_name, MissingParameter("scalar name")
            assert scalar_type, MissingParameter("scalar type")

            scalar = field.get(scalar_name, default_val)
            if scalar is None:
                scalar = default_val

            assert _is_field_type_matched(scalar, scalar_type), InvalidParameter(
                f"{scalar_name} should be type {scalar_type}, "
                f"type of {scalar_name} is:{type(scalar)}"
            )

            scalar_dic[scalar_name] = scalar

        assert len(scalar_dic) > 0, "scalar should not be empty"

        return scalar_dic


def _default_index(knowledge_schema: VikingKnowledgeBaseSchema) -> Dict[str, Any]:
    return {
        "index_type": IndexType.HNSW_HYBRID,
        "index_config": {
            "fields": [
                _default_fields_to_dict(field) for field in knowledge_schema.fields
            ],
            "cpu_quota": 1,
            "embedding_model": EmbddingModelType.EmbeddingModelBgeLargeZhAndM3,
        },
    }


class VikingKnowledgeBase(KnowledgeBase):
    collection: Collection
    client: VikingKnowledgeBaseService = pydantic.Field(default=_init_service())

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def _get_viking_knowledgebase_client(
        cls, ak: str = "", sk: str = ""
    ) -> VikingKnowledgeBaseService:
        client = getattr(cls, "client", None)
        if client is None:
            return _init_service(ak, sk)
        else:
            return cls.client

    def _fields_to_dict(self, fields: List[Field]) -> Dict[str, Any]:
        return {field.field_name: field.field_val for field in fields}

    def _set_chunk_scalars(self, point: Point) -> Dict[str, Any]:
        scalars = self._fields_to_dict(point.doc_info.fields)
        scalars["doc_id"] = point.doc_info.doc_id
        scalars["doc_type"] = point.doc_info.doc_type
        scalars["chunk_id"] = point.point_id
        return scalars

    def point_to_chunk(self, point: Point) -> KnowledgeChunk:
        return KnowledgeChunk(
            knowledge_schema=self.knowledge_schema,
            primary_key=("id", point.point_id),
            vector=("content", point.content),
            scalars=self._set_chunk_scalars(point),
            retrieve_score=point.score if point.score is not None else 0.0,
        )

    @classmethod
    def generate_sid(cls) -> str:
        import random
        import string
        from datetime import datetime

        TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
        RANDOM_LENGTH = 5

        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        random_string = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=RANDOM_LENGTH)
        )
        return f"viking_knowledgebase_{timestamp}_{random_string}"

    @classmethod
    def create(
        cls,
        schema: VikingKnowledgeBaseSchema,
        description: Optional[str] = "",
        index: Dict[str, Any] = {},
        client: Optional[VikingKnowledgeBaseService] = None,
    ) -> "VikingKnowledgeBase":
        viking_knowledgebase_client: VikingKnowledgeBaseService = (
            client or cls._get_viking_knowledgebase_client()
        )
        collection_name: str = cls.generate_sid()
        default_index = _default_index(schema)
        if len(index) != 0:
            index = _merge_dicts(default_index, index)
        else:
            index = default_index
        collection: Collection = viking_knowledgebase_client.create_collection(
            collection_name=collection_name,
            index=index,
            description=description,
        )

        return cls(
            sid=collection_name,
            knowledge_schema=schema,
            collection=collection,
            client=viking_knowledgebase_client,
        )

    @classmethod
    def delete(
        cls, sid: str, client: Optional[VikingKnowledgeBaseService] = None
    ) -> None:
        viking_knowledgebase_client: VikingKnowledgeBaseService = (
            client or cls._get_viking_knowledgebase_client()
        )
        viking_knowledgebase_client.drop_collection(collection_name=sid)

    @classmethod
    def get(
        cls,
        sid: str,
        schema: VikingKnowledgeBaseSchema,
        client: Optional[VikingKnowledgeBaseService] = None,
    ) -> "VikingKnowledgeBase":
        viking_knowledgebase_client: VikingKnowledgeBaseService = (
            client or cls._get_viking_knowledgebase_client()
        )
        collection = viking_knowledgebase_client.get_collection(collection_name=sid)

        return cls(
            sid=sid,
            knowledge_schema=schema,
            collection=collection,
            client=viking_knowledgebase_client,
        )

    @deprecated  # abstract
    def search(
        self, query: Union[str, List[Any]], count: int = 10, **kwargs: Any
    ) -> List[KnowledgeChunk]:
        if isinstance(query, str):
            filter = kwargs.get("filter", {})
            dense_weight = kwargs.get("dense_weight", 0.5)
            rerank_switch = kwargs.get("rerank_switch", False)
            query_param = {"doc_filter": filter}
            points: List[Point] = self.client.search_collection(
                collection_name=self.sid,
                query=query,
                query_param=query_param,
                limit=count,
                dense_weight=dense_weight,
                rerank_switch=rerank_switch,
            )
        else:
            raise InvalidParameter("query should be either str or list")
        chunks: List[KnowledgeChunk] = []
        for point in points:
            chunks.append(self.point_to_chunk(point))

        return chunks

    def upsert_doc(self, doc: KnowledgeDoc) -> bool:
        scalars = []
        if doc.doc_scalars is not None:
            scalars = _merge_scalars(self.knowledge_schema.scalars, doc.doc_scalars)
        else:
            for _scalar in self.knowledge_schema.scalars:
                scalars.append(
                    {
                        "field_name": _scalar["field_name"],
                        "field_type": _scalar["field_type"],
                        "field_value": _scalar["default_val"],
                    }
                )

        if doc.add_type == "tos":
            self.collection.add_doc(
                add_type=doc.add_type,
                tos_path=doc.remote_path,
            )

        elif doc.add_type == "url":
            self.collection.add_doc(
                add_type="url",
                doc_id=doc.doc_id,
                doc_name=doc.doc_name,
                doc_type=doc.type.value,
                tos_path=None,
                url=doc.remote_path,
                meta=scalars,
            )

        return True

    def batch_upsert_docs(self, tos_path: str) -> bool:
        self.collection.add_doc(
            add_type="tos",
            tos_path=tos_path,
        )
        return True

    # abstract
    def get_chunk(self, chunk_id: str) -> KnowledgeChunk:
        point: Point = self.collection.get_point(chunk_id)
        return self.point_to_chunk(point)

    def batch_get_chunks(self) -> List[KnowledgeChunk]:
        points: List[Point] = self.collection.list_points()
        return [self.point_to_chunk(point) for point in points]

    # abstract
    def delete_chunks(self, chunk_id: List[str]) -> None:
        raise KnowledgeBaseError("api not support in viking_knowledgebase")

    def batch_delete_chunks(self, chunk_ids: Union[str, List[str]]) -> bool:
        raise KnowledgeBaseError("api not support in viking_knowledgebase")

    # abstract
    def upsert_chunks(self, data: List[KnowledgeChunk]) -> bool:
        raise KnowledgeBaseError("api not support in viking_knowledgebase")

    # abstract
    async def aupsert_chunks(self, data: List[KnowledgeChunk]) -> bool:
        raise KnowledgeBaseError("api not support in viking_knowledgebase")

    # abstract
    async def adelete_chunks(self, chunk_id: List[str]) -> None:
        pass

    # abstract
    async def aget_chunk(self, chunk_id: str) -> KnowledgeChunk:
        point: Point = await self.collection.async_get_point(point_id=chunk_id)
        return self.point_to_chunk(point)

    @deprecated  # abstract
    async def asearch(
        self, query: Union[str, List[Any]], count: int = 10, **kwargs: Any
    ) -> List[KnowledgeChunk]:
        if isinstance(query, str):
            filter = kwargs.get("filter", {})
            dense_weight = kwargs.get("dense_weight", 0.5)
            rerank_switch = kwargs.get("rerank_switch", False)
            query_param = {"doc_filter": filter}
            points: List[Point] = await self.client.async_search_collection(
                collection_name=self.sid,
                query=query,
                query_param=query_param,
                limit=count,
                dense_weight=dense_weight,
                rerank_switch=rerank_switch,
            )
        else:
            raise InvalidParameter("query should be either str or list")
        chunks: List[KnowledgeChunk] = []
        for point in points:
            chunks.append(self.point_to_chunk(point))
        return chunks

    async def aupsert_doc(self, doc: KnowledgeDoc) -> bool:
        scalars = _merge_scalars(self.knowledge_schema.scalars, doc.doc_scalars)
        if doc.add_type == "tos":
            await self.collection.async_add_doc(
                add_type=doc.add_type,
                tos_path=doc.remote_path,
            )

        elif doc.add_type == "url":
            await self.collection.async_add_doc(
                add_type="url",
                doc_id=doc.doc_id,
                doc_name=doc.doc_name,
                doc_type=doc.type.value,
                tos_path=None,
                url=doc.remote_path,
                scalars=scalars,
            )

        return True

    async def abatch_get_chunks(self) -> List[KnowledgeChunk]:
        points: List[Point] = await self.collection.async_list_points()
        return [self.point_to_chunk(point) for point in points]


async def get_viking_knowledge_base_client(
    ak: str = "", sk: str = ""
) -> VikingKnowledgeBaseService:
    client_pool = get_client_pool()
    client: VikingKnowledgeBaseService = client_pool.get_client("viking-knowledgebase")  # type: ignore
    if not client:
        client = VikingKnowledgeBaseService(
            ak=ak or os.getenv("VOLC_ACCESSKEY"), sk=sk or os.getenv("VOLC_SECRETKEY")
        )
    return client
