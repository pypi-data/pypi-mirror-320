import asyncio
import base64
import hashlib
import json
import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union, get_args

import pydantic
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from pydantic import BaseModel, field_validator, model_validator
from volcengine.viking_db import (
    Collection,
    Data,
    DistanceType,
    Field,
    FieldType,
    Index,
    IndexType,
    Order,
    QuantType,
    ScalarOrder,
    Text,
    VectorIndexParams,
)

from ark.component.v3.llm.base import BaseEmbeddingLanguageModel
from ark.component.v3.vectorstores.embedding import (
    inplace_batch_update_chunk_embeddings,
    norm_l2,
)
from ark.core.client import get_client_pool
from ark.core.client.vikingdb import VikingDBClient
from ark.core.rag import KnowledgeBase, KnowledgeChunk, KnowledgeSchema
from ark.core.utils.errors import InvalidParameter, MissingParameter

RAGSchema = KnowledgeSchema
RAGBase = KnowledgeBase
MemoryChunk = KnowledgeChunk

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
    "float32": FieldType.Float32,
}

FIELD_MAP = {
    FieldType.Int64: "int64",
    FieldType.String: "string",
    FieldType.Text: "text",
    FieldType.Bool: "bool",
    FieldType.List_String: "list<string>",
    FieldType.List_Int64: "list<int64>",
    FieldType.Vector: "vector",
    FieldType.Float32: "float32",
}

ORDER_MAP = {"asc": Order.Asc, "desc": Order.Desc}


def _get_vdb_client() -> VikingDBClient:
    client_pool = get_client_pool()
    client: VikingDBClient = client_pool.get_client("vdb")  # type: ignore
    if not client:
        client = VikingDBClient()
    return client


class MemoryHandler:
    @staticmethod
    def encrypt(plaintext: str, public_key: bytes) -> str:
        plaintext_byte = plaintext.encode("utf-8")
        rsa_public_key: Any = serialization.load_pem_public_key(public_key)
        ciphertext_byte = rsa_public_key.encrypt(
            plaintext_byte,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        ciphertext_str = base64.b64encode(ciphertext_byte).decode("utf-8")
        return ciphertext_str

    @staticmethod
    def decrypt(ciphertext: str, private_key: bytes) -> str:
        ciphertext_byte = base64.b64decode(ciphertext.encode("utf-8"))
        rsa_private_key: Any = serialization.load_pem_private_key(
            private_key, password=None
        )
        plaintext_byte = rsa_private_key.decrypt(
            ciphertext_byte,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        plaintext = plaintext_byte.decode("utf-8")
        return plaintext


def _generate_id(id_str: str) -> str:
    timestamp = int(time.time() * 1000)
    text = f"{timestamp}{id_str}"
    sha256 = hashlib.sha256(text.encode())
    hex_digest = sha256.hexdigest()
    random_id = str(int(hex_digest, 16))[:11]
    return random_id


def _default_index_name(collection_name: str) -> str:
    return f"{collection_name}_Index"


def _default_index(
    client: VikingDBClient, collection_name: str, custom: Dict[str, Any] = {}
) -> Index:
    filtered_fields = _default_filtered_fields()
    scalar_index = [field.field_name for field in filtered_fields]
    scalar_index.extend([field["name"] for field in custom.get("scalars", [])])
    partition_field = _default_partition_fields()[0]

    return Index(
        collection_name=collection_name,
        index_name=_default_index_name(collection_name),
        cpu_quota=custom.get("cpu_quota", 2),
        partition_by=partition_field.field_name,
        vector_index=custom.get(
            "vector_index",
            VectorIndexParams(
                distance=DistanceType.IP,
                index_type=IndexType.HNSW,
                quant=QuantType.Int8,
            ),
        ),
        scalar_index=scalar_index,
        shard_count=custom.get("shard_count", None),
        viking_db_service=client,
        stat=None,
    )


def _default_attrs_fields() -> List[Field]:
    return [
        Field(field_name="for_mem", field_type=FieldType.Bool, default_val=True),
        Field(field_name="extra", field_type=FieldType.String, default_val=""),
        Field(
            field_name="mem_inner_success", field_type=FieldType.Bool, default_val=True
        ),
        Field(
            field_name="mem_inner_enable", field_type=FieldType.Bool, default_val=True
        ),
        Field(field_name="mem_inner_attr", field_type=FieldType.Text, default_val=""),
    ]


def _default_filtered_fields() -> List[Field]:
    return [
        Field(
            field_name="foreign_id", field_type=FieldType.List_String, default_val=[]
        ),
        Field(field_name="status", field_type=FieldType.String, default_val=""),
        Field(field_name="public", field_type=FieldType.String, default_val=""),
        Field(field_name="create_ts", field_type=FieldType.Int64, default_val=0),
        Field(field_name="update_ts", field_type=FieldType.Int64, default_val=0),
        Field(field_name="invalidate_ts", field_type=FieldType.Int64, default_val=0),
        Field(field_name="pipeline", field_type=FieldType.String, default_val=""),
        Field(field_name="time_value", field_type=FieldType.Float32, default_val=1.0),
        Field(field_name="trust_value", field_type=FieldType.Float32, default_val=1.0),
    ]


def _default_partition_fields() -> List[Field]:
    return [Field(field_name="partition", field_type=FieldType.String, default_val="")]


def _default_fields() -> List[Field]:
    default_attrs_fields = _default_attrs_fields()
    default_filtered_fields = _default_filtered_fields()
    default_partition_fields = _default_partition_fields()
    default_attrs_fields.extend(default_filtered_fields)
    default_attrs_fields.extend(default_partition_fields)
    return default_attrs_fields


def _is_valid_field_type(field_type: str) -> bool:
    for field in FieldType:
        if field_type == field.value:
            return True
    return False


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


async def get_embedding(query: str, endpoint_id: str) -> List[float]:
    llm = BaseEmbeddingLanguageModel(endpoint_id=endpoint_id, input=[query])
    embeddings = await llm.abatch()
    return embeddings[0] if len(embeddings) > 0 else []


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
    name: str
    type: str
    default_val: Optional[Any] = None

    @model_validator(mode="before")
    @classmethod
    def validate_scalar(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        field_type, default_val = v.get("type"), v.get("default_val")

        assert field_type, MissingParameter("type")
        assert _is_valid_field_type(field_type), InvalidParameter(
            f"field type {field_type} not in supported field types"
        )

        if default_val:
            assert _is_field_type_matched(default_val, field_type), InvalidParameter(
                "default_val"
            )
        return v


class VikingMemorySchema(RAGSchema):
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
        scalars = [scalar for scalar in self.scalars]
        scalars.extend(
            [
                {
                    "name": field.field_name,
                    "type": FIELD_MAP[field.field_type],
                    "default_val": field.default_val,
                }
                for field in _default_fields()
            ]
        )
        scalar_dic: Dict[str, Any] = {}
        for scalar_schema in scalars:
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

            # assert _is_field_type_matched(scalar, scalar_type), InvalidParameter(
            #     f"{scalar_name} should be type {scalar_type}, "
            #     f"type of {scalar_name} is:{type(scalar)}"
            # )

            scalar_dic[scalar_name] = scalar

        # assert len(scalar_dic) > 0, "scalar should not be empty"
        return scalar_dic


class VikingMemory(RAGBase):
    collection: Collection
    index: Index
    client: VikingDBClient = pydantic.Field(default_factory=_get_vdb_client)

    @property
    def memory_schema(self) -> KnowledgeSchema:
        return self.knowledge_schema

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def fields_to_chunk(self, fields: Dict[str, Any]) -> MemoryChunk:
        return MemoryChunk(
            knowledge_schema=self.knowledge_schema,
            primary_key=self.knowledge_schema.get_primary_key_data(fields),
            vector=self.knowledge_schema.get_vector_data(fields),
            scalars=self.knowledge_schema.get_scalar_data(fields),
        )

    @classmethod
    def chunk_to_data(cls, chunk: MemoryChunk, ttl: Optional[int] = None) -> Data:
        fields: Dict[str, Any] = {
            chunk.primary_key[0]: chunk.primary_key[1],
            chunk.vector[0]: chunk.vector[1],
        }

        for scalar in chunk.scalars.items():
            fields[scalar[0]] = scalar[1]

        fields["mem_inner_success"] = fields.get("mem_inner_success", True)
        fields["mem_inner_enable"] = fields.get("mem_inner_enable", True)
        fields["mem_inner_attr"] = fields.get("mem_inner_attr", "")
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
        return f"vm_{timestamp}_{random_string}"

    @classmethod
    def create(
        cls,
        schema: VikingMemorySchema,
        description: Optional[str] = "",
        index: Dict[str, Any] = {},
        client: Optional[VikingDBClient] = None,
    ) -> "VikingMemory":
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
        schema: VikingMemorySchema,
        client: Optional[VikingDBClient] = None,
    ) -> "VikingMemory":
        vdb_client: VikingDBClient = client or _get_vdb_client()
        collection = vdb_client.get_collection(sid)
        if collection is not None and len(collection.indexes) > 0:
            index = collection.indexes[0]
        else:
            index = vdb_client.get_index(sid, _default_index_name(sid))
        return cls(
            sid=sid,
            knowledge_schema=schema,
            collection=collection,
            client=vdb_client,
            index=index,
        )

    def upsert_chunks(self, data: List[MemoryChunk], ttl: Optional[int] = None) -> bool:
        """
        Add data to the memory
        """
        data_list: List[Data] = []
        for d in data:
            data_list.append(self.chunk_to_data(d, ttl))

        self.collection.upsert_data(data=data_list)
        return True

    def flush(
        self,
        chunks: List[MemoryChunk],
        bs: int = 50,
        retry: int = 3,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Batch flush chunk into memory
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

    def get_chunk(self, primary_key: str) -> MemoryChunk:
        """
        Get a chunk from the memory
        """

        data: Data = self.collection.fetch_data(primary_key)

        return self.fields_to_chunk(data.fields)

    def delete_chunks(self, primary_key: Union[str, List[str]]) -> None:
        """
        Delete chunk from the memory
        """

        self.collection.delete_data(primary_key)

    def batch_delete_chunks(
        self, chunk_id: List[str], bs: int = 50, retry: int = 3
    ) -> None:
        """
        Batch delete chunk from memory
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

    def search(
        self, query: Union[str, List[Any]], count: int, **kwargs: Any
    ) -> List[MemoryChunk]:
        """
        Search the memory
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
            raise InvalidParameter("query should be either str or list")
        chunks: List[MemoryChunk] = []
        for data in datas:
            chunk = self.fields_to_chunk(data.fields)
            chunk.retrieve_score = data.score
            chunks.append(chunk)

        return chunks

    async def aupsert_chunks(self, data: List[MemoryChunk]) -> bool:
        """
        Add data to the memory
        TODO: refactor with async vdb client
        """

        return await asyncio.get_running_loop().run_in_executor(
            None, self.upsert_chunks, data
        )

    async def adelete_chunks(self, primary_key: List[str]) -> None:
        await self.collection.async_delete_data(primary_key)

    async def aget_chunk(self, primary_key: str) -> MemoryChunk:
        data: Data = await self.collection.async_fetch_data(primary_key)
        memory_chunk: MemoryChunk = self.fields_to_chunk(data.fields)
        extra = memory_chunk.scalars.get("extra", None)
        if extra is not None:
            memory_chunk.scalars["extra"] = json.loads(memory_chunk.scalars["extra"])
        return memory_chunk

    # 对外暴露的API
    async def aadd(
        self,
        memory: str,
        user_id: Union[str, List[str]],
        **kwargs: Any,
    ) -> str:
        sid = self.sid
        # init primary key
        primary_key = self.memory_schema.primary_key.get("name", "")
        partition = kwargs.get("partition", "L")
        user_id_str = ""
        if isinstance(user_id, list):
            user_id_str = "-".join(user_id)
        else:
            user_id_str = user_id
            user_id = [user_id]
        random_id_str = _generate_id(user_id_str)
        primary_key_str = f"{partition}-{user_id_str}-{random_id_str}"
        # init vector
        vector_key = self.memory_schema.vector.get("name", "")
        vector = memory  # before_emb
        endpoint_id = self.memory_schema.vector.get("model", "")
        vector_dim = self.memory_schema.vector.get("dim", 0)
        # init scalar
        public_key = kwargs.get("public_key", None)
        if public_key is not None:
            memory = MemoryHandler.encrypt(memory, public_key)
        extra = kwargs.get("extra", {})
        extra["content"] = memory
        current_ts = int(time.time() * 1000)
        scalars = {
            "create_ts": current_ts,
            "update_ts": current_ts,
            "extra": json.dumps(extra, ensure_ascii=False),
            "partition": partition,
            "user_id": user_id,
        }
        ttl = kwargs.get("ttl", None)
        if ttl is not None:
            scalars["invalidate_ts"] = current_ts + ttl * 1000
        kwargs.update(scalars)

        mc = MemoryChunk(
            primary_key=(primary_key, primary_key_str),
            vector=(vector_key, vector),
            scalars=kwargs,
        )

        try:
            chunks = await inplace_batch_update_chunk_embeddings(
                chunks=[mc], endpoint_id=endpoint_id, norm="l2", vector_dim=vector_dim
            )
        except Exception:
            error_string = traceback.format_exc()
            LOGGER.error(
                "请求 embedding 失败, 知识库 id: %s, 错误信息: %s", sid, error_string
            )
            return ""

        try:
            self.flush(chunks=chunks, ttl=ttl)
        except Exception:
            error_string = traceback.format_exc()
            LOGGER.error("导入失败, 记忆库 id: %s, 错误信息: %s", sid, error_string)
            return ""

        LOGGER.info("导入成功, 记忆库 id: %s", sid)
        return primary_key_str

    async def asearch(
        self, query: Union[str, List[Any]], count: int = 10, **kwargs: Any
    ) -> List[MemoryChunk]:
        endpoint_id = self.memory_schema.vector.get("model", "")
        vector_dim = self.memory_schema.vector.get("dim", 0)

        if isinstance(query, str):
            query_vector = await get_embedding(query=query, endpoint_id=endpoint_id)
        else:
            query_vector = query

        if vector_dim > 0 and len(query_vector) != vector_dim:
            query_vector = query_vector[:vector_dim]

        query_vector = norm_l2(query_vector)

        dsl_filter = kwargs.get("dsl_filter", None)
        partition = kwargs.get("partition", "L")

        datas: List[Data] = await self.index.async_search_by_vector(
            vector=query_vector,
            limit=count,
            filter=dsl_filter,
            partition=partition,
        )

        memory_chunks: List[KnowledgeChunk] = []
        for data in datas:
            chunk = self.fields_to_chunk(data.fields)
            chunk.retrieve_score = data.score
            memory_chunks.append(chunk)

        private_key = kwargs.get("private_key", None)
        for i in range(len(memory_chunks)):
            extra = memory_chunks[i].scalars.get("extra", None)
            if extra is not None:
                if private_key is not None:
                    memory_chunks[i].scalars["extra"][
                        "content"
                    ] = MemoryHandler.decrypt(
                        ciphertext=extra["content"], private_key=private_key
                    )

                memory_chunks[i].scalars["extra"] = json.loads(
                    memory_chunks[i].scalars["extra"]
                )

        return memory_chunks

    async def asearch_by_scalar(
        self, field_name: str, count: int = 10, order: str = "asc", **kwargs: Any
    ) -> List[MemoryChunk]:
        scalar_order = ScalarOrder(
            field_name=field_name, order=ORDER_MAP.get(order, "")
        )
        dsl_filter = kwargs.get("dsl_filter", None)
        partition = kwargs.get("partition", None)
        output_fields = kwargs.get("output_fields", None)
        datas: List[Data] = await self.index.async_search(
            order=scalar_order,
            limit=count,
            filter=dsl_filter,
            output_fields=output_fields,
            partition=partition,
        )

        memory_chunks: List[MemoryChunk] = []
        for data in datas:
            chunk = self.fields_to_chunk(data.fields)
            chunk.retrieve_score = data.score
            memory_chunks.append(chunk)

        private_key = kwargs.get("private_key", None)
        for i in range(len(memory_chunks)):
            extra = memory_chunks[i].scalars.get("extra", None)
            if extra is not None:
                if private_key is not None:
                    memory_chunks[i].scalars["extra"][
                        "content"
                    ] = MemoryHandler.decrypt(
                        ciphertext=extra["content"], private_key=private_key
                    )

                memory_chunks[i].scalars["extra"] = json.loads(
                    memory_chunks[i].scalars["extra"]
                )

        return memory_chunks

    async def aupdate_memory(self, memory: str, primary_key: str, **kwargs: Any) -> str:
        data: Data = await self.collection.async_fetch_data(id=primary_key)
        chunk: MemoryChunk = self.fields_to_chunk(data.fields)
        chunk.scalars.update(kwargs)
        extra: dict = kwargs.get("extra", {})

        public_key = kwargs.get("public_key", None)
        if public_key is not None:
            extra["content"] = MemoryHandler.encrypt(
                plaintext=extra["content"], public_key=public_key
            )
        extra["content"] = memory

        current_ts = int(time.time() * 1000)
        chunk.scalars.update(
            {
                "update_ts": current_ts,
                "extra": json.dumps(extra, ensure_ascii=False),
            }
        )
        ttl = kwargs.get("ttl", None)
        if ttl is not None:
            chunk.scalars["invalidate_ts"] = current_ts + ttl * 1000
        vector_key = self.memory_schema.vector.get("name", "")
        vector = memory  # before_emb
        chunk.vector = (vector_key, vector)
        try:
            endpoint_id = self.memory_schema.vector.get("model", "")
            vector_dim = self.memory_schema.vector.get("dim", 0)
            chunks = await inplace_batch_update_chunk_embeddings(
                chunks=[chunk],
                endpoint_id=endpoint_id,
                norm="l2",
                vector_dim=vector_dim,
            )
        except Exception:
            error_string = traceback.format_exc()
            LOGGER.error(
                "请求 embedding 失败, 知识库 id: %s, 错误信息: %s",
                self.sid,
                error_string,
            )
            return ""

        try:
            self.flush(chunks=chunks, ttl=ttl)
        except Exception:
            error_string = traceback.format_exc()
            LOGGER.error(
                "导入失败, 记忆库 id: %s, 错误信息: %s", self.sid, error_string
            )
            return ""

        return primary_key

    adelete_memory = adelete_chunks
    aget_memory = aget_chunk
