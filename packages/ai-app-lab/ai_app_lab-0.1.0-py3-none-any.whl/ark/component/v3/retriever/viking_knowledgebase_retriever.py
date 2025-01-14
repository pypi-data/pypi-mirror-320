from abc import ABC
from typing import Any, List, Union

from ark.component.retriever.base_retriever import BaseRetriever
from ark.component.v3.vectorstores.viking_knowledgebase import (
    VikingKnowledgeBase,
    VikingKnowledgeBaseSchema,
)
from ark.core.rag import KnowledgeChunk
from ark.core.utils.errors import InvalidParameter


class VikingKnowledgeBaseRetriever(BaseRetriever, ABC):
    def __init__(
        self, config: VikingKnowledgeBaseSchema, db: VikingKnowledgeBase
    ) -> None:
        self.config = config
        self.db = db

    async def retrieve(
        self,
        query: Union[str, List[float]],
        retrieve_count: int,
        *args: Any,
        **kwargs: Any,
    ) -> List[KnowledgeChunk]:
        dsl_filter = kwargs.get("dsl_filter")
        if isinstance(query, str):
            return await self.db.asearch(query, retrieve_count, filter=dsl_filter)
        else:
            raise InvalidParameter("viking_knowledgebase search query is str")
