from typing import List

from langchain_core.output_parsers import BaseTransformOutputParser


class RagIntentMessageChunkOutputParser(BaseTransformOutputParser[bool]):
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
        """Parse the output of the resource_id into a bool.

        Args:
            text (str): The output of the resource_id.

        Returns:
            Tuple(bool, str): The bool indicating whether to search.
                True, return empty str
                False, return direct answer
        """
        if "无需检索" in text:
            return False
        return True


class RagRewriteMessageChunkOutputParser(BaseTransformOutputParser[str]):
    """OutputParser that parses BaseMessageChunk into intent of whether to search."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    @property
    def _type(self) -> str:
        """Return the output parser type for serialization."""
        return "default"

    def parse(self, text: str) -> str:
        """Parse the output of the resource_id into a bool."""
        return text.strip()


class RagRewriteOutputParser(BaseTransformOutputParser[List[str]]):
    """Parse llm output to List[str]"""

    def parse(self, text: str) -> List[str]:
        queries = text.split("\n")
        # filter extreme shot query
        return [q.strip() for q in queries if len(q) > 3]
