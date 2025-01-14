from abc import abstractmethod
from typing import Any, Optional, TypeVar, Union

from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import BasePromptTemplate
from pydantic.v1 import BaseModel, Field
from volcenginesdkarkruntime import AsyncArk

from ark.core.client import ArkClient, get_client_pool
from ark.core.runnable import Runnable


def _default_ark_client() -> ArkClient:
    client_pool = get_client_pool()
    client: ArkClient = client_pool.get_client("chat")  # type: ignore
    if not client:
        client = ArkClient()
    return client


T = TypeVar("T")


class BaseLanguageModel(BaseModel, Runnable[T]):
    endpoint_id: str
    client: Union[ArkClient, AsyncArk] = Field(default_factory=_default_ark_client)
    template: Optional[BasePromptTemplate] = None
    output_parser: Optional[BaseOutputParser] = None

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
