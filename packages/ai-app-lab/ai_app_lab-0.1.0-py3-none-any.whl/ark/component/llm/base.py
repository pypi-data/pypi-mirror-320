from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from langchain_core.output_parsers import BaseTransformOutputParser
from langchain_core.prompts import BaseChatPromptTemplate

from ark.core.idl.common_protocol import Embedding, Parameters
from ark.core.idl.maas_protocol import (
    MaasChatMessage,
    MaasChatRequest,
    MaasChatResponse,
    MaasClassificationRequest,
    MaasClassificationResponse,
    MaasEmbeddingsRequest,
    MaasEmbeddingsResponse,
    MaasTokenizeRequest,
    MaasTokenizeResponse,
)
from ark.core.llm import BaseLanguageModel
from ark.core.task import task
from ark.core.utils.prompt import format_maas_prompts


class BaseChatLanguageModel(BaseLanguageModel[MaasChatResponse]):
    messages: List[MaasChatMessage]
    parameters: Optional[Union[Parameters, Dict[str, Any]]] = None
    template: Optional[BaseChatPromptTemplate] = None
    output_parser: Optional[BaseTransformOutputParser] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def generate_prompts(
        self, messages: List[MaasChatMessage], **kwargs: Any
    ) -> List[MaasChatMessage]:
        if not self.template:
            return messages

        return format_maas_prompts(self.template, messages, **kwargs)

    @task()
    def parse_output(self, text: str) -> Any:
        if not self.output_parser:
            return text

        return self.output_parser.parse(text)

    @task()
    async def aparse_output(self, text: str) -> Any:
        if not self.output_parser:
            return text

        return await self.output_parser.aparse(text)

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

    async def arun(self, *args: Any, **kwargs: Any) -> MaasChatResponse:
        request = MaasChatRequest(
            messages=self.generate_prompts(self.messages, **kwargs),
            parameters=self.parameters,
            **kwargs,
        )

        return await self._arun(self.endpoint_id, request)

    async def astream(
        self, *args: Any, **kwargs: Any
    ) -> AsyncIterator[MaasChatResponse]:
        request = MaasChatRequest(
            stream=True,
            messages=self.generate_prompts(self.messages, **kwargs),
            parameters=self.parameters,
            **kwargs,
        )

        async for resp in await self._arun(self.endpoint_id, request):
            yield resp

    def run(self, *args: Any, **kwargs: Any) -> MaasChatResponse:
        request = MaasChatRequest(
            messages=self.generate_prompts(self.messages, **kwargs),
            parameters=self.parameters,
            **kwargs,
        )
        return self._run(self.endpoint_id, request)

    def stream(self, **kwargs: Any) -> Iterator[MaasChatResponse]:
        request = MaasChatRequest(
            stream=True,
            messages=self.generate_prompts(self.messages, **kwargs),
            parameters=self.parameters,
            **kwargs,
        )

        for resp in self._run(self.endpoint_id, request):
            yield resp


class BaseEmbeddingLanguageModel(BaseLanguageModel[Embedding]):
    input: Union[str, List[str]]
    encoding_format: Optional[str] = None
    user: Optional[str] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @task()
    async def _arun(
        self,
        endpoint_id: str,
        request: MaasEmbeddingsRequest,
    ) -> MaasEmbeddingsResponse:
        return await self.client.async_embeddings(endpoint_id=endpoint_id, req=request)

    @task()
    def _run(
        self, endpoint_id: str, request: MaasEmbeddingsRequest
    ) -> MaasEmbeddingsResponse:
        return self.client.embeddings(endpoint_id=endpoint_id, req=request.model_dump())

    async def arun(self, *args: Any, **kwargs: Any) -> MaasEmbeddingsResponse:
        input = [self.input] if isinstance(self.input, str) else self.input

        request = MaasEmbeddingsRequest(
            input=input, encoding_format=self.encoding_format, user=self.user, **kwargs
        )

        return await self._arun(self.endpoint_id, request)

    def run(self, *args: Any, **kwargs: Any) -> MaasEmbeddingsResponse:
        input = [self.input] if isinstance(self.input, str) else self.input

        request = MaasEmbeddingsRequest(
            input=input, encoding_format=self.encoding_format, user=self.user, **kwargs
        )

        return self._run(self.endpoint_id, request)

    def batch(self, *args: Any, **kwargs: Any) -> List[Embedding]:
        assert isinstance(self.input, list)

        request = MaasEmbeddingsRequest(
            input=self.input,
            encoding_format=self.encoding_format,
            user=self.user,
            **kwargs,
        )

        resp = self._run(self.endpoint_id, request)
        return resp.data

    async def abatch(self, *args: Any, **kwargs: Any) -> List[Embedding]:
        assert isinstance(self.input, list)

        request = MaasEmbeddingsRequest(
            input=self.input,
            encoding_format=self.encoding_format,
            user=self.user,
            **kwargs,
        )

        resp = await self._arun(self.endpoint_id, request)
        return resp.data


class BaseTokenizeLanguageModel(BaseLanguageModel):
    endpoint_id: str
    text: str

    @task()
    async def _arun(
        self,
        endpoint_id: str,
        request: MaasTokenizeRequest,
    ) -> MaasTokenizeResponse:
        return await self.client.async_tokenize(endpoint_id, req=request)

    @task()
    def _run(
        self, endpoint_id: str, request: MaasTokenizeRequest
    ) -> MaasTokenizeResponse:
        return self.client.tokenize(endpoint_id, req=request.model_dump())

    async def arun(self, *args: Any, **kwargs: Any) -> MaasTokenizeResponse:
        request = MaasTokenizeRequest(text=self.text)

        return await self._arun(self.endpoint_id, request)

    def run(self, *args: Any, **kwargs: Any) -> MaasTokenizeResponse:
        request = MaasTokenizeRequest(text=self.text)

        return self._run(self.endpoint_id, request)


class BaseClassificationLanguageModel(BaseLanguageModel):
    query: str
    labels: List[str]

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @task()
    async def _arun(
        self,
        endpoint_id: str,
        request: MaasClassificationRequest,
    ) -> MaasClassificationResponse:
        return await self.client.async_classification(
            endpoint_id=endpoint_id, req=request
        )

    @task()
    def _run(
        self,
        endpoint_id: str,
        request: MaasClassificationRequest,
    ) -> MaasClassificationResponse:
        return self.client.classification(
            endpoint_id=endpoint_id, req=request.model_dump()
        )

    async def arun(self, *args: Any, **kwargs: Any) -> Any:
        request = MaasClassificationRequest(
            query=self.query, labels=self.labels, **kwargs
        )

        return await self._arun(self.endpoint_id, request)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        request = MaasClassificationRequest(
            query=self.query, labels=self.labels, **kwargs
        )

        return self._run(self.endpoint_id, request)
