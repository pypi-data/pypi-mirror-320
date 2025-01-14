from abc import ABC, abstractmethod
from typing import Any, List, Union

from ark.core.rag import KnowledgeChunk


class BaseRetriever(ABC):
    """
    This class is used to retrieve chunks from KnowledgeBase.
    """

    @abstractmethod
    async def retrieve(
        self,
        query: Union[str, List[float]],
        retrieve_count: int,
        *args: Any,
        **kwargs: Any,
    ) -> List[KnowledgeChunk]:
        """
        Retrieve KnowledgeChunk from KnowledgeBase.
        Returns: top n similar chunks
        """
