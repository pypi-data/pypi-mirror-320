import hashlib
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator

ACCEPTED_SCHEMES = {"tos", "http", "https"}


class DocType(Enum):
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "md"
    HTML = "html"
    CSV = "csv"
    JSONL = "jonsl"
    UNDEFINED = "undefined"
    PPTX = "pptx"


class KnowledgeDoc(BaseModel):
    """
    This class is used to handle a doc
    """

    local_path: Optional[str] = None
    remote_path: Optional[str] = None
    type: DocType
    encoding: str = "utf-8"
    _doc_id: Optional[str] = None

    doc_name: str = ""
    add_type: str = "url"
    doc_scalars: Optional[List[Dict[str, Any]]] = None

    @property
    def doc_id(self) -> str:
        if self._doc_id:
            return self._doc_id
        if self.remote_path:
            self._doc_id = hashlib.md5(self.remote_path.encode("utf-8")).hexdigest()
        elif self.local_path:
            file_name = self.local_path.split("/")[-1]
            self._doc_id = hashlib.md5(file_name.encode("utf-8")).hexdigest()
        else:
            raise ValueError("local_path and remote_path are both None")
        return self._doc_id
        # return self.doc_scalars['doc_id']

    @field_validator("remote_path")
    @classmethod
    def validate_remote_path(cls, v: Any) -> Optional[str]:
        """check if the remote_path is tos"""
        if v is None:
            return None
        result = urlparse(v)
        if result.scheme not in ACCEPTED_SCHEMES:
            raise ValueError("remote_path must be tos or http or https")
        return v

    @field_validator("local_path")
    @classmethod
    def validate_local_path(cls, v: Any) -> Optional[str]:
        """check if the local_path exists"""
        if v is None:
            return None
        os.path.exists(v)
        return v


class KnowledgeSchema(BaseModel, ABC):
    """
    This class describe Knowledge base index structure
    """

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    primary_key: Dict[str, str]
    vector: Dict[str, Any]
    scalars: List[Dict[str, Any]]

    vector_text_len_limit: int = 500

    @field_validator("primary_key")
    @abstractmethod
    def validate_primary_key(cls, v: Dict[str, str]) -> Dict[str, str]:
        pass

    @field_validator("vector")
    @abstractmethod
    def validate_vector(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @field_validator("scalars")
    @abstractmethod
    def validate_scalars(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def get_primary_key_data(self, field: Dict[str, Any]) -> Tuple[str, Any]:
        pass

    @abstractmethod
    def get_vector_data(
        self, field: Dict[str, Any]
    ) -> Tuple[str, Union[List[Any], str]]:
        pass

    @abstractmethod
    def get_scalar_data(self, field: Dict[str, Any]) -> Dict[str, Any]:
        pass


class KnowledgeChunk(BaseModel):
    """
    This class is used to handle a chunk
    """

    primary_key: Tuple[str, Any]
    vector: Tuple[str, Union[List[Any], str]]
    scalars: Dict[str, Any]
    retrieve_score: float = 0.0
    knowledge_schema: Optional[KnowledgeSchema] = None


class KnowledgeBase(BaseModel, ABC):
    """
    This main class
    """

    sid: str
    knowledge_schema: KnowledgeSchema

    @abstractmethod
    def upsert_chunks(self, data: List[KnowledgeChunk]) -> bool:
        """
        Add data to the knowledge base
        """
        pass

    @abstractmethod
    def get_chunk(self, chunk_id: str) -> KnowledgeChunk:
        """
        Get a chunk from the knowledge base
        """
        pass

    @abstractmethod
    def delete_chunks(self, chunk_id: List[str]) -> None:
        """
        Delete chunkfrom the knowledge base
        """
        pass

    @abstractmethod
    def search(
        self, query: Union[str, List[Any]], count: int, **kwargs: Any
    ) -> List[KnowledgeChunk]:
        """
        Search the knowledge base
        """
        pass

    @abstractmethod
    async def aupsert_chunks(self, data: List[KnowledgeChunk]) -> bool:
        """
        Add data to the knowledge base
        """
        pass

    @abstractmethod
    async def aget_chunk(self, chunk_id: str) -> KnowledgeChunk:
        """
        Get a chunk from the knowledge base
        """
        pass

    @abstractmethod
    async def adelete_chunks(self, chunk_id: List[str]) -> None:
        """
        Delete chunkfrom the knowledge base
        """
        pass

    @abstractmethod
    async def asearch(
        self, query: Union[str, List[Any]], count: int, **kwargs: Any
    ) -> List[KnowledgeChunk]:
        """
        Search the knowledge base
        """
        pass
