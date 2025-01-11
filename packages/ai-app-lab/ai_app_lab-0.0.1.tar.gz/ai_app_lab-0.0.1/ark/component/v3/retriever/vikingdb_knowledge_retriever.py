import asyncio
import os
from typing import Any, Dict, List, Optional, Union

from volcengine.viking_knowledgebase import VikingKnowledgeBaseService
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


@task()
async def retrieve_knowledge(
    action_config: Dict[str, Any],
    req: MaasChatRequest,
    client: VikingKnowledgeBaseService,
    keywords: Optional[List[str]] = None,
) -> KnowledgeBaseResponse:
    collection_name, cnt, show_reference, project = (
        action_config.get("collection_name", ""),
        action_config.get("retrieve_count", 0),
        action_config.get("show_reference", True),
        action_config.get("project", "default"),
    )

    if not collection_name:
        raise MissingParameter("collection_name")
    if not cnt:
        raise MissingParameter("retrieve_count")

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

    retriever = VikingDBRetriever(
        config=viking_knowledgebase_schema,
        collection_name=collection_name,
        project=project,
        kn_client=client,
    )

    try:
        retrieve_results = await asyncio.gather(
            *[
                retriever.retrieve(
                    query=query[:1024], retrieve_count=cnt, dsl_filter=None
                )
                for query in queries
            ]
        )
    except VikingKnowledgeBaseServerException as e:
        raise KnowledgeBaseError(e.message)

    topk_chunks = [chunk for result in retrieve_results for chunk in result]
    # Format Reference
    refs: List[str] = []
    references: List[Reference] = []
    for chunk in topk_chunks:
        meta_text = (
            f"文档ID：{chunk.scalars['doc_id']}\n"
            + f"文档名：{chunk.scalars['doc_name']}\n"
            + f"文档类型：{chunk.scalars['doc_type']}\n"
            + f"文档标题：{chunk.scalars['doc_title']}\n"
            + f"分块标题：{chunk.scalars['chunk_title']}\n"
            + f"分块编号：{chunk.primary_key[1]}\n"
        )
        text = {chunk.vector[1]}
        refs.append(f"{meta_text}\n正文：\n{text}\n")

        if show_reference:
            references.append(
                Reference(
                    collection_name=collection_name,
                    chunk_id=chunk.primary_key[1],
                    chunk_title=chunk.scalars["chunk_title"],
                    doc_id=chunk.scalars["doc_id"],
                    doc_name=chunk.scalars["doc_name"],
                    doc_type=chunk.scalars["doc_type"],
                    doc_title=chunk.scalars["doc_title"],
                    project=project,
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

    retriever = VikingDBRetriever(
        config=viking_knowledgebase_schema,
        collection_name=request.collection_name,
        project=request.project,
        kn_client=client,
    )

    try:
        retrieve_results = await asyncio.gather(
            *[
                retriever.retrieve(
                    query=keyword[:1024],
                    retrieve_count=request.retrieve_count,
                    dsl_filter=None,
                )
                for keyword in keywords
            ]
        )
    except VikingKnowledgeBaseServerException as e:
        raise errorsv3.KnowledgeBaseError(e.message)

    # Format Reference
    texts: List[str] = []
    references: List[Reference] = []
    topk_chunks = [chunk for result in retrieve_results for chunk in result]
    for chunk in topk_chunks:
        texts.append(chunk.vector[1])
        if request.show_reference:
            references.append(
                Reference(
                    collection_name=request.collection_name,
                    chunk_id=chunk.primary_key[1],
                    chunk_title=chunk.scalars["chunk_title"],
                    doc_id=chunk.scalars["doc_id"],
                    doc_name=chunk.scalars["doc_name"],
                    doc_type=chunk.scalars["doc_type"],
                    doc_title=chunk.scalars["doc_title"],
                    project=request.project,
                )
            )

    return ArkKnowledgeBaseResponse(
        texts=texts,
        references=references,
    )
