from abc import ABC, abstractmethod
from typing import Any, List

from ark.core.rag import KnowledgeChunk, KnowledgeDoc


class BaseReader(ABC):
    """
    This class is used to parse and chunk origin data
    """

    @abstractmethod
    def load(
        self, doc: KnowledgeDoc, *args: Any, **kwargs: Any
    ) -> List[KnowledgeChunk]:
        """
        Load data into KnowledgeChunk objects.
        Returns: split chunks of the document
        """
        pass
