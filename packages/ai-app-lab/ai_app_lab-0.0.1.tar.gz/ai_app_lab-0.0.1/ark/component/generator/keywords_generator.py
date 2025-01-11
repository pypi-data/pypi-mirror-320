from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from langchain.prompts.chat import BaseChatPromptTemplate
from langchain.schema.output_parser import BaseTransformOutputParser
from pydantic.v1 import BaseModel, Field

from ark.component.output_parser.browsing_output import (
    BrowsingGenerationMessageChunkOutputParser,
)
from ark.component.prompts import BrowsingGenerationChatPromptTemplate
from ark.core._api.deprecation import deprecated
from ark.core.client import ArkClient, Client, get_client_pool
from ark.core.idl.common_protocol import Parameters
from ark.core.idl.maas_protocol import (
    MaasChatMessage,
    MaasChatRequest,
    MaasChatResponse,
)
from ark.core.task import task
from ark.core.utils.prompt import format_maas_prompts


def _get_ark_client() -> Optional[Client]:
    client_pool = get_client_pool()
    client = client_pool.get_client("chat")
    if not client:
        client = ArkClient()
    return client


def _get_default_prompt_template() -> BaseChatPromptTemplate:
    return BrowsingGenerationChatPromptTemplate()


def _get_default_output_parser() -> BaseTransformOutputParser:
    return BrowsingGenerationMessageChunkOutputParser()


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.BrowsingQueryRewrite",
)
class KeywordsGenerator(BaseModel):
    endpoint_id: str
    messages: List[MaasChatMessage]
    parameters: Optional[Union[Parameters, Dict[str, Any]]] = None
    options: Optional[Dict[str, Any]] = None
    client: ArkClient = Field(default_factory=_get_ark_client)
    template: BaseChatPromptTemplate = Field(
        default_factory=_get_default_prompt_template
    )
    output_parser: BaseTransformOutputParser[List[str]] = Field(
        default_factory=_get_default_output_parser
    )

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def generate_prompts(
        self, messages: List[MaasChatMessage], **kwargs: Any
    ) -> List[MaasChatMessage]:
        return format_maas_prompts(self.template, messages, **kwargs)

    def parse_output(self, text: str) -> List[str]:
        return self.output_parser.parse(text)

    async def aparse_output(self, output: str) -> List[str]:
        return await self.output_parser.aparse(output)

    @task()
    async def _arun(
        self,
        endpoint_id: str,
        request: MaasChatRequest,
    ) -> Union[AsyncIterator[MaasChatResponse], MaasChatResponse]:
        if request.stream:
            return await self.client.async_stream_chat(
                endpoint_id=endpoint_id, req=request
            )
        else:
            return await self.client.async_chat(endpoint_id=endpoint_id, req=request)

    @task()
    def _run(
        self, endpoint_id: str, request: MaasChatRequest
    ) -> Union[Iterator[MaasChatResponse], MaasChatResponse]:
        if request.stream:
            return self.client.stream_chat(endpoint_id=endpoint_id, req=request)
        else:
            return self.client.chat(endpoint_id=endpoint_id, req=request.model_dump())

    async def arun(self, **kwargs: Any) -> MaasChatResponse:
        request = MaasChatRequest(
            messages=self.generate_prompts(self.messages, **kwargs),
            parameters=self.parameters,
        )

        return await self._arun(self.endpoint_id, request)

    async def astream(self, **kwargs: Any) -> AsyncIterator[MaasChatResponse]:
        request = MaasChatRequest(
            stream=True,
            messages=self.generate_prompts(self.messages, **kwargs),
            parameters=self.parameters,
        )

        async for resp in await self._arun(self.endpoint_id, request):
            yield resp

    def run(self, **kwargs: Any) -> MaasChatResponse:
        request = MaasChatRequest(
            messages=self.generate_prompts(self.messages, **kwargs),
            parameters=self.parameters,
        )
        return self._run(self.endpoint_id, request)

    def stream(self, **kwargs: Any) -> Iterator[MaasChatResponse]:
        request = MaasChatRequest(
            stream=True,
            messages=self.generate_prompts(self.messages, **kwargs),
            parameters=self.parameters,
        )

        for resp in self._run(self.endpoint_id, request):
            yield resp
