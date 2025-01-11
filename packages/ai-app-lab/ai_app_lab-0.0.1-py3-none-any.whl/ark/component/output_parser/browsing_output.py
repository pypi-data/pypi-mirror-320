import re
from typing import Iterable, List, get_args

from langchain.schema.output_parser import BaseTransformOutputParser

from ark.core.idl.maas_protocol import SOURCE_TAG, SourceType


class BrowsingIntentMessageChunkOutputParser(BaseTransformOutputParser[bool]):
    """OutputParser that parses BaseMessageChunk into intent of whether to search."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    @property
    def _type(self) -> str:
        """Return the output parser type for serialization."""
        return "default"

    def parse(self, text: str) -> bool:
        """Returns the input text with no changes."""
        return text == "需要"


class BrowsingGenerationMessageChunkOutputParser(BaseTransformOutputParser[List[str]]):
    """OutputParser that parses BaseMessageChunk into list of str."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    @property
    def _type(self) -> str:
        """Return the output parser type for serialization."""
        return "default"

    def parse(self, text: str) -> List[str]:
        """Returns the input text with no changes."""
        return text.split("[next]")


class MultiIntentionOutputParser(BaseTransformOutputParser[Iterable[str]]):
    """Parse llm output to bool"""

    source_type: List[SourceType]

    def parse(self, text: str) -> Iterable[str]:
        for source in get_args(SourceType):
            if source not in self.source_type:
                continue
            tag = SOURCE_TAG[source]
            if tag in text:
                yield source


class SearchRewriteOutputParser(BaseTransformOutputParser[List[str]]):
    """Parse llm output to List[str]"""

    def parse(self, text: str) -> List[str]:
        result = re.sub(r"^\d+\.\s-?\s?|\-\s", "", text, flags=re.MULTILINE)
        queries = result.split("\n")
        # filter extreme shot query
        return [q.strip() for q in queries if len(q) >= 2]
