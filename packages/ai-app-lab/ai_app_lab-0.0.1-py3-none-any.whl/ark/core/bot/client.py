from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple, Union

import httpx
from httpx import AsyncClient, Timeout
from typing_extensions import Literal
from volcengine.ApiInfo import ApiInfo
from volcengine.maas.v2.utils import gen_req_id
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime._base_client import make_request_options
from volcenginesdkarkruntime._constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
)
from volcenginesdkarkruntime._exceptions import ArkAPIError
from volcenginesdkarkruntime._streaming import Stream
from volcenginesdkarkruntime.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionStreamOptionsParam,
    ChatCompletionToolParam,
    completion_create_params,
)

from ark.core.client import APIGAuthorization, Client
from ark.core.idl.ark_protocol import ArkChatCompletionChunk, ArkChatResponse


class BotClient(Client, Ark):
    def __init__(
        self,
        *,
        base_url: str,
        ak: str | None = None,
        sk: str | None = None,
        jwt_token: str | None = None,
        api_path: str = "/api/v3/bots/chat/completions",
        auto_refresh_apikey: bool = True,
        timeout: float | Timeout | None = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: AsyncClient | None = None,
    ):
        super().__init__(
            ak=ak,
            sk=sk,
            api_key=jwt_token,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        self.authorization = None
        if auto_refresh_apikey:
            self.service_id, region = self.parse_apig_host(base_url)
            self.auto_refresh_apikey = auto_refresh_apikey
            self.authorization = APIGAuthorization(ak=ak, sk=sk)
        self.api_info = self.get_api_info(api_path)

    @staticmethod
    def get_api_info(api_path: str) -> Dict[str, ApiInfo]:
        api_info = {
            "chat": ApiInfo("POST", api_path, {}, {}, {}),
        }
        return api_info

    @staticmethod
    def parse_apig_host(base_url: str) -> Tuple[str, str]:
        if not isinstance(base_url, str):
            raise ArkAPIError("base_url is invalid")

        import re

        # base_url format: https://{apig service id}.apigateway-{region}.volceapi.com/
        pattern = r"https://([\w.-]+)\.apigateway-([\w.-])+\.volceapi\.com.*"

        matches = re.match(pattern, base_url)

        if matches and len(matches.group()) >= 2:
            matched_groups = matches.groups()
            service_id, region = matched_groups[0], matched_groups[1]
            return service_id, region
        else:
            raise ArkAPIError("a parameter is missing: service_id")

    def _validate(self) -> None:
        if self.api_key is None and (self.sk is None or self.sk is None):
            raise ArkAPIError("api_key or ak/sk is required")

    def authorize(
        self,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        self._validate()

        if self.authorization:
            self.api_key = self.authorization.get_apikey(service_id=self.service_id)
        if not extra_headers:
            extra_headers = {}
        extra_headers["Authorization"] = f"Bearer {self.api_key}"
        extra_headers["X-Client-Request-Id"] = gen_req_id()
        return extra_headers

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    def create_chat_completions(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: str,
        frequency_penalty: Optional[float] | None = None,
        function_call: completion_create_params.FunctionCall | None = None,
        functions: Iterable[completion_create_params.Function] | None = None,
        logit_bias: Optional[Dict[str, int]] | None = None,
        logprobs: Optional[bool] | None = None,
        max_tokens: Optional[int] | None = None,
        presence_penalty: Optional[float] | None = None,
        stop: Union[Optional[str], List[str]] | None = None,
        stream: Optional[Literal[False]] | Literal[True] | None = None,
        stream_options: Optional[ChatCompletionStreamOptionsParam] | None = None,
        temperature: Optional[float] | None = None,
        tools: Iterable[ChatCompletionToolParam] | None = None,
        top_logprobs: Optional[int] | None = None,
        top_p: Optional[float] | None = None,
        user: str | None = None,
        metadata: Dict[str, object] | None = None,
        extra_headers: Dict[str, str] | None = None,
        extra_query: Dict[str, object] | None = None,
        extra_body: Dict[str, object] | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> Union[ArkChatResponse, Stream[ArkChatCompletionChunk]]:
        api_info = self.api_info.get(
            "chat", ApiInfo("POST", "/api/v3/bots/chat/completions", {}, {}, {})
        )

        extra_headers = self.authorize(extra_headers)

        response = self.chat.completions._post(
            api_info.path,
            body={
                "messages": messages,
                "model": model,
                "frequency_penalty": frequency_penalty,
                "function_call": function_call,
                "functions": functions,
                "logit_bias": logit_bias,
                "logprobs": logprobs,
                "max_tokens": max_tokens,
                "presence_penalty": presence_penalty,
                "stop": stop,
                "stream": stream,
                "stream_options": stream_options,
                "temperature": temperature,
                "tools": tools,
                "top_logprobs": top_logprobs,
                "top_p": top_p,
                "user": user,
                "metadata": metadata,
            },
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=ArkChatResponse,
            stream=stream or False,
            stream_cls=Stream[ArkChatCompletionChunk],
        )

        return response
