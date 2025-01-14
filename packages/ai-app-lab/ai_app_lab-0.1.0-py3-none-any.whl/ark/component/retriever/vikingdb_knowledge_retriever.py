import asyncio
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from volcengine.viking_knowledgebase import Point, VikingKnowledgeBaseService
from volcengine.viking_knowledgebase.exception import VikingKnowledgeBaseServerException

import ark.core.utils.errorsv3 as errorsv3
from ark.component.retriever.base_retriever import BaseRetriever
from ark.component.vectorstores.vikingdb import VikingDBSchema
from ark.core.client import get_client_pool
from ark.core.idl.ark_protocol import ArkKnowledgeBaseRequest, ArkKnowledgeBaseResponse
from ark.core.idl.common_protocol import ChatRole, Reference
from ark.core.idl.maas_protocol import KnowledgeBaseResponse, MaasChatRequest
from ark.core.rag import KnowledgeChunk
from ark.core.task.task import task
from ark.core.utils.context import get_reqid
from ark.core.utils.errors import KnowledgeBaseError, MissingParameter
from ark.core.utils.types import snake_merge

viking_knowledgebase_schema = VikingDBSchema(
    primary_key={
        "name": "id",
        "type": "string",
        "default_val": "",
    },
    vector={
        "name": "content",
        "type": "text",
        "model": "text_bge_large_zh",
        "embedding_type": "vdb",
    },
    scalars=[
        {
            "name": "doc_id",
            "type": "string",
            "default_val": "",
        },
        {
            "name": "doc_name",
            "type": "string",
            "default_val": "",
        },
        {
            "name": "doc_type",
            "type": "string",
            "default_val": "",
        },
        {
            "name": "doc_title",
            "type": "string",
            "default_val": "",
        },
        {
            "name": "chunk_title",
            "type": "string",
            "default_val": "",
        },
    ],
    vector_text_len_limit=500,
)


def _get_viking_knowledge_client() -> VikingKnowledgeBaseService:
    client_pool = get_client_pool()
    client: VikingKnowledgeBaseService = client_pool.get_client("viking-knowledgebase")  # type: ignore
    if not client:
        client = VikingKnowledgeBaseService(
            ak=os.getenv("VOLC_ACCESSKEY"), sk=os.getenv("VOLC_SECRETKEY")
        )
    return client


class VikingDBRetriever(BaseRetriever):
    def __init__(
        self,
        config: VikingDBSchema,
        kn_client: VikingKnowledgeBaseService,
        collection_name: str,
        project: str = "default",
    ) -> None:
        if not kn_client:
            kn_client = _get_viking_knowledge_client()
        self.config = config
        self.kn_client = kn_client
        self.collection_name = collection_name
        self.project = project

    @task()
    async def retrieve(
        self,
        query: Union[str, List[float]],
        retrieve_count: int,
        dsl_filter: Optional[Any] = None,
        partition: str = "default",
        norm: str = "none",
        vector_dim: int = 0,
    ) -> List[KnowledgeChunk]:
        if dsl_filter:
            db_filter = dsl_filter
        else:
            db_filter = None

        self.kn_client.setHeader({"x-tt-logid": get_reqid()})
        points = await self.kn_client.async_search_collection(
            self.collection_name,
            query,
            query_param=db_filter,
            limit=retrieve_count,
            project=self.project,
        )
        chunks: List[KnowledgeChunk] = []
        for point in points:
            fields = {
                "id": point.point_id,
                "chunk_title": point.chunk_title,
                "content": point.content,
                "doc_id": point.doc_info.doc_id,
                "doc_name": point.doc_info.doc_name,
                "doc_type": point.doc_info.doc_type,
                "doc_title": point.doc_info.doc_name,
            }
            chunk = KnowledgeChunk(
                knowledge_schema=self.config,
                primary_key=self.config.get_primary_key_data(fields),
                vector=self.config.get_vector_data(fields),
                scalars=self.config.get_scalar_data(fields),
            )
            chunks.append(chunk)
        return chunks


def _transform_retrieve_parameters(action_config: Dict[str, Any]) -> Dict[str, Any]:
    if "retrieve_count" in action_config:
        action_config["limit"] = action_config.pop("retrieve_count")
    if "rerank_retrieve_count" in action_config:
        action_config["retrieve_count"] = action_config.pop("rerank_retrieve_count")
    return action_config


@task()
async def retrieve_knowledge(
    action_config: Dict[str, Any],
    req: MaasChatRequest,
    client: VikingKnowledgeBaseService,
    keywords: Optional[List[str]] = None,
) -> KnowledgeBaseResponse:
    config = ArkKnowledgeBaseRequest(**action_config)

    if keywords and len(keywords) > 0:
        queries = keywords
    else:
        contents: List[str] = []
        for message in req.messages:
            if message.role == ChatRole.USER and isinstance(message.content, str):
                contents.append(message.content)
        if len(contents) > 0:
            queries = [contents[-1]]
        else:
            raise MissingParameter("query")

    try:
        client.setHeader({"x-tt-logid": get_reqid()})
        retrieve_results: Tuple[List[Point]] = await asyncio.gather(
            *[
                client.async_search_collection(
                    query=query[:1024],
                    **_transform_retrieve_parameters(
                        config.model_dump(
                            exclude_unset=True,
                            exclude_none=True,
                            exclude={"question", "keywords", "show_reference"},
                        )
                    ),
                )
                for query in queries
            ]
        )
    except VikingKnowledgeBaseServerException as e:
        raise KnowledgeBaseError(e.message)

    topk_chunks = snake_merge(retrieve_results)
    refs: List[str] = []
    references: List[Reference] = []
    for chunk in topk_chunks:
        refs.append(chunk.content)

        references.append(
            Reference(
                collection_name=chunk.collection_name,
                chunk_id=str(chunk.chunk_id)
                if chunk.chunk_id is not None
                else chunk.point_id,
                chunk_title=chunk.chunk_title,
                doc_id=chunk.doc_id,
                doc_name=chunk.doc_info.doc_name,
                doc_type=chunk.doc_info.doc_type,
                doc_title=chunk.doc_info.title,
                project=chunk.project,
            )
        )

    return KnowledgeBaseResponse(
        texts=refs,
        references=references,
    )


@task()
async def retrieve_viking_knowledge(
    request: ArkKnowledgeBaseRequest,
    client: VikingKnowledgeBaseService,
) -> ArkKnowledgeBaseResponse:
    keywords = [request.question]
    if request.keywords and len(request.keywords) > 0:
        keywords = request.keywords

    try:
        client.setHeader({"x-tt-logid": get_reqid()})
        retrieve_results: Tuple[List[Point]] = await asyncio.gather(
            *[
                client.async_search_collection(
                    query=query[:1024],
                    **_transform_retrieve_parameters(
                        request.model_dump(
                            exclude_unset=True,
                            exclude_none=True,
                            exclude={"question", "keywords", "show_reference"},
                        )
                    ),
                )
                for query in keywords
            ]
        )
    except VikingKnowledgeBaseServerException as e:
        raise errorsv3.KnowledgeBaseError(e.message)

    topk_chunks: List[Point] = snake_merge(retrieve_results)
    texts: List[str] = []
    references: List[Reference] = []
    for chunk in topk_chunks:
        texts.append(chunk.content)

        references.append(
            Reference(
                collection_name=chunk.collection_name,
                chunk_id=str(chunk.chunk_id)
                if chunk.chunk_id is not None
                else chunk.point_id,
                chunk_title=chunk.chunk_title,
                doc_id=chunk.doc_id,
                doc_name=chunk.doc_info.doc_name,
                doc_type=chunk.doc_info.doc_type,
                doc_title=chunk.doc_info.title,
                project=chunk.project,
            )
        )

    return ArkKnowledgeBaseResponse(
        texts=texts,
        references=references,
    )
