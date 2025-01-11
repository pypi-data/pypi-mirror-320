import copy
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from httpx import Timeout
from langchain.prompts.chat import BaseChatPromptTemplate
from langchain.schema.output_parser import BaseTransformOutputParser
from pydantic import BaseModel
from pydantic.v1 import Field
from typing_extensions import Literal
from volcenginesdkarkruntime import Ark, AsyncArk
from volcenginesdkarkruntime._streaming import AsyncStream
from volcenginesdkarkruntime.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
)
from volcenginesdkarkruntime.types.create_embedding_response import (
    CreateEmbeddingResponse,
)
from volcenginesdkarkruntime.types.create_tokenization_response import (
    CreateTokenizationResponse,
    Tokenization,
)

from ark.core.client import get_client_pool
from ark.core.idl.ark_protocol import (
    ArkChatCompletionChunk,
    ArkChatParameters,
    ArkChatRequest,
    ArkChatResponse,
    ArkMessage,
    CallableFunction,
    EndpointId,
    FunctionCallMode,
)
from ark.core.idl.common_protocol import ActionDetails, BotUsage
from ark.core.llm import BaseLanguageModel
from ark.core.task import task
from ark.core.utils.context import get_extra_headers
from ark.core.utils.prompt import format_ark_prompts
from ark.core.utils.types import convert_response_message, transform_response


def _default_ark_client() -> AsyncArk:
    client_pool = get_client_pool()
    client: AsyncArk = client_pool.get_client("ark")  # type: ignore
    if not client:
        client = AsyncArk(timeout=Timeout(connect=1.0, timeout=60.0))
    return client


class BaseChatLanguageModel(
    BaseLanguageModel[Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]]
):
    client: AsyncArk = Field(default_factory=_default_ark_client)
    messages: List[ArkMessage]
    parameters: Optional[ArkChatParameters] = None
    template: Optional[BaseChatPromptTemplate] = None
    output_parser: Optional[BaseTransformOutputParser] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def generate_prompts(
        self,
        messages: List[ArkMessage],
        *,
        additional_system_prompts: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[ArkMessage]:
        # additional system prompts would be put at first
        if additional_system_prompts:
            prompts = [
                ArkMessage(role="system", content=system_prompt)
                for system_prompt in additional_system_prompts
            ]
            prompts.extend(messages)
            messages = prompts

        if not self.template:
            return messages

        return format_ark_prompts(self.template, messages, **kwargs)

    def get_request_model(self, **kwargs: Any) -> EndpointId:
        return self.endpoint_id

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
        request: ArkChatRequest,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]:
        assert isinstance(self.client, AsyncArk), TypeError("Invalid Client for v3 sdk")

        params = request.get_chat_request(extra_body)

        extra_headers = get_extra_headers(extra_headers)

        return await self.client.chat.completions.create(
            **params,
            extra_headers=extra_headers,
            extra_query=extra_query,
        )

    @task()
    def _run(
        self,
        request: ArkChatRequest,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]:
        sync_client = Ark()

        extra_headers = get_extra_headers(extra_headers)

        return sync_client.chat.completions.create(
            **request.get_chat_request(extra_body),
            extra_headers=extra_headers,
            extra_query=extra_query,
        )

    def run(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        parameters = (
            self.parameters.model_dump(exclude_none=True, exclude_unset=True)
            if self.parameters
            else {}
        )
        request = ArkChatRequest(
            stream=False,
            messages=self.generate_prompts(self.messages, **kwargs),
            model=self.get_request_model(**kwargs),
            **parameters,
        )

        completion = self._run(request, extra_headers, extra_query, extra_body)
        return ArkChatResponse(**completion.__dict__)

    def stream(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        parameters = (
            self.parameters.model_dump(exclude_none=True, exclude_unset=True)
            if self.parameters
            else {}
        )
        request = ArkChatRequest(
            stream=True,
            messages=self.generate_prompts(self.messages, **kwargs),
            model=self.get_request_model(**kwargs),
            **parameters,
        )

        completion = self._run(request, extra_headers, extra_query, extra_body)
        for resp in completion:
            yield ArkChatCompletionChunk(**resp.__dict__)

    async def handle_function_call(
        self,
        request: ArkChatRequest,
        response: Union[
            ChatCompletionChunk, ChatCompletion, ArkChatCompletionChunk, ArkChatResponse
        ],
        available_functions: Optional[Dict[str, CallableFunction]] = None,
        function_call_mode: Optional[FunctionCallMode] = FunctionCallMode.SEQUENTIAL,
    ) -> bool:
        return await handle_function_call(
            request, response, available_functions, function_call_mode
        )

    async def arun(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        *,
        available_functions: Optional[Dict[str, CallableFunction]] = None,
        function_call_mode: Optional[FunctionCallMode] = FunctionCallMode.SEQUENTIAL,
        additional_system_prompts: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ArkChatResponse:
        parameters = (
            self.parameters.model_dump(exclude_none=True, exclude_unset=True)
            if self.parameters
            else {}
        )
        request = ArkChatRequest(
            stream=False,
            messages=self.generate_prompts(
                self.messages,
                additional_system_prompts=additional_system_prompts,
                **kwargs,
            ),
            model=self.get_request_model(**kwargs),
            **parameters,
        )
        responses = []
        while True:
            completion: ChatCompletion = await self._arun(
                request, extra_headers, extra_query, extra_body
            )
            responses.append(completion)

            if completion.choices and completion.choices[0].finish_reason:
                if not await self.handle_function_call(
                    request, completion, available_functions, function_call_mode
                ):
                    break

        return ArkChatResponse.merge(responses)

    async def astream(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        *,
        available_functions: Optional[Dict[str, CallableFunction]] = None,
        function_call_mode: Optional[FunctionCallMode] = FunctionCallMode.SEQUENTIAL,
        additional_system_prompts: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> AsyncStream[ArkChatCompletionChunk]:
        parameters = (
            self.parameters.model_dump(exclude_none=True, exclude_unset=True)
            if self.parameters
            else {}
        )
        request = ArkChatRequest(
            stream=True,
            messages=self.generate_prompts(
                self.messages,
                additional_system_prompts=additional_system_prompts,
                **kwargs,
            ),
            model=self.get_request_model(**kwargs),
            **parameters,
        )

        usage_chunks, cumulated = [], []
        while True:
            completion = await self._arun(
                request, extra_headers, extra_query, extra_body
            )
            # default: one iter
            is_more_request = False
            async for resp in completion:  # type: ChatCompletionChunk
                if resp.usage:
                    usage_chunks.append(resp)
                else:
                    # cumulated chunks is used for caculator/fc inner cot output
                    cumulated.append(resp)
                    yield ArkChatCompletionChunk(**resp.__dict__)

                if resp.choices and resp.choices[0].finish_reason:
                    ark_resp = ArkChatCompletionChunk(**resp.__dict__).merge(cumulated)
                    # clear after used
                    cumulated = []
                    is_more_request = await self.handle_function_call(
                        request, ark_resp, available_functions, function_call_mode
                    )
                    if (
                        request.stream_options
                        and request.stream_options.get("include_usage") is True
                    ):
                        usage_chunks.append(ark_resp)

            if not is_more_request:
                break

        if len(usage_chunks) > 0:
            yield ArkChatCompletionChunk.merge(usage_chunks)


@task()
async def handle_function_call(
    request: ArkChatRequest,
    response: Union[
        ChatCompletionChunk, ChatCompletion, ArkChatCompletionChunk, ArkChatResponse
    ],
    available_functions: Optional[Dict[str, CallableFunction]] = None,
    function_call_mode: Optional[FunctionCallMode] = FunctionCallMode.SEQUENTIAL,
    **kwargs: Any,
) -> bool:
    if response.choices[0].finish_reason != "tool_calls":
        return False

    response_message = (
        response.choices[0].delta
        if isinstance(response, ChatCompletionChunk)
        or isinstance(response, ArkChatCompletionChunk)
        else response.choices[0].message
    )
    tool_calls = response_message.tool_calls

    if not tool_calls or not available_functions:
        return False

    function_call_mode = function_call_mode or FunctionCallMode.SEQUENTIAL
    if function_call_mode != FunctionCallMode.SEQUENTIAL:
        raise NotImplementedError("Only sequential function call mode is supported")

    request.messages.append(convert_response_message(response_message))

    function_calls = copy.deepcopy(tool_calls)
    for tool_call in function_calls:
        function_name = tool_call.function.name

        function_to_call = available_functions.get(function_name)
        original_function_response: Union[
            Union[str, BaseModel], Tuple[Union[str, BaseModel], ActionDetails]
        ] = ""
        if function_to_call:
            function_args = json.loads(tool_call.function.arguments)
            original_function_response = await function_to_call(function_args, **kwargs)
        else:
            logging.error(f"Function {function_name} not found")

        if (
            isinstance(original_function_response, tuple)
            and len(original_function_response) == 2
            and isinstance(original_function_response[1], ActionDetails)
        ):
            function_response, action_detail = original_function_response
            if isinstance(response, ArkChatCompletionChunk):
                response.bot_usage = BotUsage(action_details=[action_detail])
        else:
            function_response = original_function_response

        request.messages.append(
            ArkMessage(
                role="tool",
                content=transform_response(function_response),
                tool_call_id=tool_call.id,
            )
        )
    return True


class BaseEmbeddingLanguageModel(BaseLanguageModel[List[float]]):
    client: AsyncArk = Field(default_factory=_default_ark_client)
    input: Union[str, List[str]]
    encoding_format: Literal["float", "base64"] = "float"
    user: Optional[str] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @task()
    async def _arun(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> CreateEmbeddingResponse:
        extra_headers = get_extra_headers(extra_headers)

        return await self.client.embeddings.create(
            model=self.endpoint_id,
            input=self.input,
            encoding_format=self.encoding_format,
            user=self.user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
        )

    @task()
    def _run(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> CreateEmbeddingResponse:
        sync_client = Ark()

        extra_headers = get_extra_headers(extra_headers)

        return sync_client.embeddings.create(
            model=self.endpoint_id,
            input=self.input,
            encoding_format=self.encoding_format,
            user=self.user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
        )

    async def arun(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> CreateEmbeddingResponse:
        return await self._arun(extra_headers, extra_query, extra_body)

    def run(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> CreateEmbeddingResponse:
        return self._run(extra_headers, extra_query, extra_body)

    def batch(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> List[List[float]]:
        resp: CreateEmbeddingResponse = self._run(
            extra_headers, extra_query, extra_body
        )
        embeddings = []
        for data in resp.data:
            embeddings.append(data.embedding)
        return embeddings

    async def abatch(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> List[List[float]]:
        resp: CreateEmbeddingResponse = await self._arun(
            extra_headers, extra_query, extra_body
        )
        embeddings = []
        for data in resp.data:
            embeddings.append(data.embedding)
        return embeddings


class BaseTokenizeLanguageModel(BaseLanguageModel[Tokenization]):
    client: AsyncArk = Field(default_factory=_default_ark_client)
    text: Union[str, List[str]]
    user: Optional[str] = None

    @task()
    async def _arun(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> CreateTokenizationResponse:
        extra_headers = get_extra_headers(extra_headers)

        return await self.client.tokenization.create(
            model=self.endpoint_id,
            text=self.text,
            user=self.user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
        )

    @task()
    def _run(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> CreateTokenizationResponse:
        sync_client = Ark()

        extra_headers = get_extra_headers(extra_headers)

        return sync_client.tokenization.create(
            model=self.endpoint_id,
            text=self.text,
            user=self.user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
        )

    async def arun(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> CreateTokenizationResponse:
        return await self._arun(extra_headers, extra_query, extra_body)

    def run(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> CreateTokenizationResponse:
        return self._run(extra_headers, extra_query, extra_body)

    def batch(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> List[Tokenization]:
        resp: CreateTokenizationResponse = self._run(
            extra_headers, extra_query, extra_body
        )
        return resp.data

    async def abatch(
        self,
        extra_headers: Optional[Dict[str, str]] = {},
        extra_query: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> List[Tokenization]:
        resp: CreateTokenizationResponse = await self._arun(
            extra_headers, extra_query, extra_body
        )
        return resp.data
