from abc import ABC
from typing import Any, Dict, List, Optional, Union

from ark.component.v3.llm.base import BaseEmbeddingLanguageModel
from ark.component.v3.retriever.base_retriever import BaseRetriever
from ark.component.v3.vectorstores.embedding import norm_l2
from ark.component.v3.vectorstores.vikingdb import VikingDB, VikingDBSchema
from ark.core.rag import KnowledgeChunk


class VikingDBRetriever(BaseRetriever, ABC):
    def __init__(self, config: VikingDBSchema, db: VikingDB) -> None:
        self.config = config
        self.db = db
        self._embedding_cache: Dict[str, Any] = {}

    async def get_embedding(self, query: str) -> List[float]:
        if query in self._embedding_cache:
            return self._embedding_cache[query]

        llm = BaseEmbeddingLanguageModel(
            endpoint_id=self.config.vector.get("model") or "", input=[query]
        )
        embeddings = await llm.abatch()
        self._embedding_cache[query] = embeddings[0] if len(embeddings) > 0 else []
        return self._embedding_cache[query]

    async def retrieve(
        self,
        query: Union[str, List[float]],
        retrieve_count: int,
        dsl_filter: Optional[Any] = None,
        partition: str = "default",
        norm: str = "none",
        vector_dim: int = 0,
        instruct: str = "为这个句子生成表示以用于检索相关文章：",
    ) -> List[KnowledgeChunk]:
        if dsl_filter:
            db_filter = dsl_filter
        else:
            db_filter = None
        if isinstance(query, str) and self.config.vector.get("embedding_type") == "llm":
            sliced_emb = await self.get_embedding(instruct + query)
            if vector_dim > 0 and len(sliced_emb) != vector_dim:
                # need vector slice & norm
                sliced_emb = sliced_emb[:vector_dim]
            if norm == "l2":
                emb_query = norm_l2(sliced_emb)
            else:
                emb_query = sliced_emb
            return await self.db.asearch(
                query=emb_query,
                count=retrieve_count,
                filter=db_filter,
                partition=partition,
            )
        return await self.db.asearch(
            query=query, count=retrieve_count, filter=db_filter, partition=partition
        )

    async def chunk_diffusion(
        self,
        query: Union[str, List[Any]],
        chunk: KnowledgeChunk,
        partition: str = "default",
        match_scalars: List[str] = ["chunk_type", "doc_id"],
        forward_diffusion: int = 1,
        backward_diffusion: int = 1,
    ) -> List[KnowledgeChunk]:
        retrieve_count = forward_diffusion + backward_diffusion + 1
        conds = [
            {
                "op": "must",
                "field": field_name,
                "conds": [chunk.scalars[field_name]],
            }
            for field_name in match_scalars
        ]
        conds.append(
            {
                "op": "range",
                "field": "chunk_id",
                "gte": max(chunk.scalars["chunk_id"] - backward_diffusion, 0),
                "lt": chunk.scalars["chunk_id"] + forward_diffusion + 1,
            }
        )
        db_filter = {"op": "and", "conds": conds}
        if isinstance(query, str) and self.config.vector.get("embedding_type") == "llm":
            emb_query = await self.get_embedding(query)
            return await self.db.asearch(
                query=emb_query,
                count=retrieve_count,
                filter=db_filter,
                partition=partition,
            )
        return await self.db.asearch(
            query=query, count=retrieve_count, filter=db_filter, partition=partition
        )
