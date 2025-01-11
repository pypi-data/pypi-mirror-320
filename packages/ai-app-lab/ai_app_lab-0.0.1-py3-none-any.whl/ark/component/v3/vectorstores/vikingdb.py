import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union, get_args

import pydantic
from pydantic import BaseModel, field_validator, model_validator
from volcengine.viking_db import (
    Collection,
    Data,
    DistanceType,
    Field,
    FieldType,
    Index,
    IndexType,
    QuantType,
    Text,
    VectorIndexParams,
)

from ark.core.client import get_client_pool
from ark.core.client.vikingdb import VikingDBClient
from ark.core.rag import KnowledgeBase, KnowledgeChunk, KnowledgeSchema
from ark.core.task.task import task
from ark.core.utils.errorsv3 import InvalidParameter, MissingParameter

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)

INSTANCE_TYPE = {
    "int64": int,
    "float32": float,
    "string": str,
    "bool": bool,
    "text": str,
}

LIST_TYPE = {
    "list<string>": List[str],
    "list<int64>": List[int],
    "vector": List[Any],
}

FIELD_ENUM_MAP = {
    "int64": FieldType.Int64,
    "string": FieldType.String,
    "text": FieldType.Text,
    "bool": FieldType.Bool,
    "list<string>": FieldType.List_String,
    "list<int64>": FieldType.List_Int64,
    "vector": FieldType.Vector,
}


def _get_vdb_client() -> VikingDBClient:
    client_pool = get_client_pool()
    client: VikingDBClient = client_pool.get_client("vdb")  # type: ignore
    if not client:
        client = VikingDBClient()
    return client


def _default_index_name(collection_name: str) -> str:
    return f"{collection_name}_Index"


def _default_index(
    client: VikingDBClient, collection_name: str, custom: Dict[str, Any] = {}
) -> Index:
    return Index(
        collection_name=collection_name,
        index_name=_default_index_name(collection_name),
        cpu_quota=custom.get("cpu_quota", 2),
        partition_by=custom.get("partition_by", ""),
        vector_index=custom.get(
            "vector_index",
            VectorIndexParams(
                distance=DistanceType.IP,
                index_type=IndexType.HNSW,
                quant=QuantType.Int8,
            ),
        ),
        scalar_index=custom.get("scalar_index", None),
        shard_count=custom.get("shard_count", None),
        viking_db_service=client,
        stat=None,
    )


def _default_fields() -> List[Field]:
    return [
        Field(
            field_name="kb_inner_success", field_type=FieldType.Bool, default_val=False
        ),
        Field(
            field_name="kb_inner_enable", field_type=FieldType.Bool, default_val=True
        ),
        Field(field_name="kb_inner_attr", field_type=FieldType.Text, default_val=""),
    ]


def _is_field_type_matched(obj: Any, expected_type: str) -> bool:
    field_type = INSTANCE_TYPE.get(expected_type)
    if field_type:
        if expected_type == "text":
            return isinstance(obj, dict) or isinstance(obj, field_type)
            # vdb lagacy
        return isinstance(obj, field_type)

    list_type = LIST_TYPE.get(expected_type)
    item_type = get_args(list_type)

    is_list_type_matched = isinstance(obj, list) and all(
        isinstance(item, item_type) for item in obj
    )
    return is_list_type_matched


def _is_valid_field_type(field_type: str) -> bool:
    for field in FieldType:
        if field_type == field.value:
            return True
    return False


class PrimaryKey(BaseModel):
    name: str
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, field_type: str) -> str:
        assert _is_valid_field_type(field_type), InvalidParameter(
            parameter=field_type,
            cause=f"field type {field_type} not in supported field types",
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

        assert field_type, MissingParameter(parameter="type")
        assert model, MissingParameter(parameter="model")
        assert embedding_type in ("vdb", "llm"), InvalidParameter(
            parameter="embedding_type"
        )
        assert _is_valid_field_type(field_type), InvalidParameter(
            parameter=field_type,
            cause=f"field type {field_type} not in supported field types",
        )

        if dim:
            assert 4 <= dim <= 2048, InvalidParameter(
                parameter="dim", cause="dim should be in range [4,2048]"
            )
            assert dim % 4 == 0, InvalidParameter(
                parameter="dim", cause="dim should be dived by 4"
            )

        return v


class Scalar(BaseModel):
    name: str
    type: str
    default_val: Optional[Any] = None

    @model_validator(mode="before")
    @classmethod
    def validate_scalar(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        field_type, default_val = v.get("type"), v.get("default_val")

        assert field_type, MissingParameter("type")
        assert _is_valid_field_type(field_type), InvalidParameter(
            parameter=field_type,
            cause=f"field type {field_type} not in supported field types",
        )

        if default_val:
            assert _is_field_type_matched(default_val, field_type), InvalidParameter(
                parameter="default_val"
            )
        return v


class VikingDBSchema(KnowledgeSchema):
    """
    This class describe vikingDB index structure
    """

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
        fields: List[Field] = _default_fields()

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
            parameter="primary_key", cause=f"primary_key should be type {key_type}"
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
                parameter="vector", cause=f"vector should be type {vector_type}"
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
                parameter="scalar",
                cause=f"{scalar_name} should be type {scalar_type}, "
                f"type of {scalar_name} is:{type(scalar)}",
            )

            scalar_dic[scalar_name] = scalar

        assert len(scalar_dic) > 0, "scalar should not be empty"

        return scalar_dic


class VikingDB(KnowledgeBase):
    """
    This class is used to store index data into vdb
    """

    collection: Collection
    index: Index
    client: VikingDBClient = pydantic.Field(default_factory=_get_vdb_client)

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def fields_to_chunk(self, fields: Dict[str, Any]) -> KnowledgeChunk:
        return KnowledgeChunk(
            knowledge_schema=self.knowledge_schema,
            primary_key=self.knowledge_schema.get_primary_key_data(fields),
            vector=self.knowledge_schema.get_vector_data(fields),
            scalars=self.knowledge_schema.get_scalar_data(fields),
        )

    @classmethod
    def chunk_to_data(cls, chunk: KnowledgeChunk, ttl: Optional[int] = None) -> Data:
        fields: Dict[str, Any] = {
            chunk.primary_key[0]: chunk.primary_key[1],
            chunk.vector[0]: chunk.vector[1],
        }

        for scalar in chunk.scalars.items():
            fields[scalar[0]] = scalar[1]

        fields["kb_inner_success"] = fields.get("kb_inner_success", True)
        fields["kb_inner_enable"] = fields.get("kb_inner_enable", True)
        fields["kb_inner_attr"] = fields.get("kb_inner_attr", "")
        return Data(fields=fields, TTL=ttl)

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
        return f"vdb_{timestamp}_{random_string}"

    @classmethod
    def create(
        cls,
        schema: VikingDBSchema,
        description: Optional[str] = "",
        index: Dict[str, Any] = {},
        client: Optional[VikingDBClient] = None,
    ) -> "VikingDB":
        vdb_client: VikingDBClient = client or _get_vdb_client()

        collection_name: str = cls.generate_sid()
        fields = schema.fields

        collection: Collection = vdb_client.create_collection(
            collection_name, fields, description=description
        )

        new_index = _default_index(
            client=vdb_client, collection_name=collection_name, custom=index
        )

        vdb_index: Index = vdb_client.create_index(
            collection_name=collection_name,
            index_name=new_index.index_name,
            vector_index=new_index.vector_index,
            cpu_quota=new_index.cpu_quota,
            description=new_index.description,
            partition_by=new_index.partition_by,
            scalar_index=new_index.scalar_index,
            shard_count=new_index.shard_count,
        )

        return cls(
            sid=collection_name,
            knowledge_schema=schema,
            collection=collection,
            client=vdb_client,
            index=vdb_index,
        )

    @classmethod
    def delete(cls, sid: str, client: Optional[VikingDBClient] = None) -> None:
        """
        Delete the knowledge collection
        """
        vdb_client: VikingDBClient = client or _get_vdb_client()
        return vdb_client.drop_collection(sid)

    @classmethod
    def get(
        cls,
        sid: str,
        schema: VikingDBSchema,
        index_name: Optional[str] = None,
        client: Optional[VikingDBClient] = None,
    ) -> "VikingDB":
        vdb_client: VikingDBClient = client or _get_vdb_client()
        collection = vdb_client.get_collection(sid)

        index = vdb_client.get_index(sid, index_name or _default_index_name(sid))

        return cls(
            sid=sid,
            knowledge_schema=schema,
            collection=collection,
            client=vdb_client,
            index=index,
        )

    def upsert_chunks(
        self, data: List[KnowledgeChunk], ttl: Optional[int] = None
    ) -> bool:
        """
        Add data to the knowledge base
        """
        data_list: List[Data] = []
        for d in data:
            data_list.append(self.chunk_to_data(d, ttl))

        self.collection.upsert_data(data=data_list)
        return True

    def flush(
        self,
        chunks: List[KnowledgeChunk],
        bs: int = 50,
        retry: int = 3,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Batch flush chunk into knowledge base
        """
        # TODO: 需要事务性支持，需要VDB实现批量刷新接口
        for i in range(0, len(chunks), bs):
            succ = False
            for r in range(retry):
                try:
                    succ = self.upsert_chunks(chunks[i : i + bs], ttl)
                except Exception as e:
                    LOGGER.error("upsert_data error, retry: %d, err: %s", r, e)
                    time.sleep(1)
                    continue
                break
            if not succ:
                raise Exception("upsert_data error after retry")
                # FIXME: raise proper Exception

    def get_chunk(self, primary_key: str) -> KnowledgeChunk:
        """
        Get a chunk from the knowledge base
        """

        data: Data = self.collection.fetch_data(primary_key)

        return self.fields_to_chunk(data.fields)

    def delete_chunks(self, primary_key: Union[str, List[str]]) -> None:
        """
        Delete chunk from the knowledge base
        """

        self.collection.delete_data(primary_key)

    def batch_delete_chunks(
        self, chunk_id: List[str], bs: int = 50, retry: int = 3
    ) -> None:
        """
        Batch delete chunk from knowledge base
        """
        # TODO: 需要事务性支持，需要VDB实现批量删除接口
        for i in range(int(len(chunk_id) / bs) + 1):
            for r in range(retry):
                try:
                    if (i + 1) * bs <= len(chunk_id):
                        self.delete_chunks(chunk_id[i * bs : (i + 1) * bs])
                    elif i * bs < len(chunk_id):
                        self.delete_chunks(chunk_id[i * bs :])
                    else:
                        break
                except Exception as e:
                    LOGGER.error("upsert_data error, retry: %d, err: %s", r, e)
                    time.sleep(0.1)
                    continue
                break

    async def aflush(
        self,
        chunks: List[KnowledgeChunk],
        bs: int = 50,
        retry: int = 3,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Batch flush chunk into knowledge base
        """
        # TODO: 需要事务性支持，需要VDB实现批量刷新接口
        for i in range(0, len(chunks), bs):
            succ = False
            for r in range(retry):
                try:
                    succ = await self.aupsert_chunks(chunks[i : i + bs], ttl)
                except Exception as e:
                    LOGGER.error("upsert_data error, retry: %d, err: %s", r, e)
                    await asyncio.sleep(1)
                    continue
                break
            if not succ:
                raise Exception("upsert_data error after retry")
                # FIXME: raise proper Exception

    async def abatch_delete_chunks(
        self, chunk_id: List[str], bs: int = 50, retry: int = 3
    ) -> None:
        """
        Batch delete chunk from knowledge base
        """
        # TODO: 需要事务性支持，需要VDB实现批量删除接口
        for i in range(int(len(chunk_id) / bs) + 1):
            for r in range(retry):
                try:
                    if (i + 1) * bs <= len(chunk_id):
                        await self.adelete_chunks(chunk_id[i * bs : (i + 1) * bs])
                    elif i * bs < len(chunk_id):
                        await self.adelete_chunks(chunk_id[i * bs :])
                    else:
                        break
                except Exception as e:
                    LOGGER.error("upsert_data error, retry: %d, err: %s", r, e)
                    await asyncio.sleep(0.1)
                    continue
                break

    def search(
        self, query: Union[str, List[Any]], count: int, **kwargs: Any
    ) -> List[KnowledgeChunk]:
        """
        Search the knowledge base
        """

        if isinstance(query, list):
            datas: List[Data] = self.index.search_by_vector(
                vector=query, limit=count, **kwargs
            )
        elif isinstance(query, str):
            datas = self.index.search_by_text(
                text=Text(text=query), limit=count, **kwargs
            )
        else:
            raise InvalidParameter(
                parameter="query", cause="query should be either str or list"
            )
        chunks: List[KnowledgeChunk] = []
        for data in datas:
            chunk = self.fields_to_chunk(data.fields)
            chunk.retrieve_score = data.score
            chunks.append(chunk)

        return chunks

    async def aupsert_chunks(
        self, data: List[KnowledgeChunk], ttl: Optional[int] = None
    ) -> bool:
        """
        Add data to the knowledge base
        """

        data_list: List[Data] = []
        for d in data:
            data_list.append(self.chunk_to_data(d, ttl))

        await self.collection.async_upsert_data(data=data_list)
        return True

    async def aget_chunk(self, primary_key: str) -> KnowledgeChunk:
        """
        Get a chunk from the knowledge base
        """
        data: Data = await self.collection.async_fetch_data(primary_key)

        return self.fields_to_chunk(data.fields)

    async def adelete_chunks(self, primary_key: List[str]) -> None:
        """
        Delete chunkfrom the knowledge base
        """
        return await self.collection.async_delete_data(primary_key)

    @task()
    async def asearch(
        self, query: Union[str, List[Any]], count: int, **kwargs: Any
    ) -> List[KnowledgeChunk]:
        if isinstance(query, list):
            datas: List[Data] = await self.index.async_search_by_vector(
                vector=query, limit=count, **kwargs
            )
        elif isinstance(query, str):
            datas = await self.index.async_search_by_text(
                text=Text(text=query), limit=count, **kwargs
            )
        else:
            raise InvalidParameter(
                parameter="query", cause="query should be either str or list"
            )
        chunks: List[KnowledgeChunk] = []
        for data in datas:
            chunk = self.fields_to_chunk(data.fields)
            chunk.retrieve_score = data.score
            chunks.append(chunk)
        return chunks
