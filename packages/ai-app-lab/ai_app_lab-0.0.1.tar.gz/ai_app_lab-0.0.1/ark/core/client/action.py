from __future__ import annotations

from typing import Any, AsyncIterable, Dict, Optional, Type, Union

import httpx
from httpx import URL, AsyncClient, Timeout
from volcengine.ApiInfo import ApiInfo
from volcenginesdkarkruntime import AsyncArk
from volcenginesdkarkruntime._base_client import make_request_options
from volcenginesdkarkruntime._constants import (
    BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
)
from volcenginesdkarkruntime._resource import AsyncAPIResource
from volcenginesdkarkruntime._streaming import AsyncStream

from ark.core.client.authorization import ArkAuthorization
from ark.core.client.base import Client
from ark.core.idl.ark_protocol import ArkActionMeta, ArkToolMeta
from ark.core.idl.common_protocol import RequestType, ResponseType
from ark.core.utils.context import get_extra_headers
from ark.core.utils.errorsv3 import AuthenticationError, InvalidParameter


class AsyncTool(AsyncAPIResource):
    async def init(
        self,
        meta_info: Union[ArkActionMeta, ArkToolMeta],
    ) -> None:
        pass

    async def create(
        self,
        path: str,
        stream: bool,
        request: RequestType,
        response_cls: Type[ResponseType],
        extra_headers: Dict[str, str] | None = None,
        extra_query: Dict[str, object] | None = None,
        extra_body: Dict[str, object] | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> Dict[str, Any] | AsyncStream[Dict[str, Any]]:
        return await self._post(
            path,
            body=request.model_dump(exclude_unset=True, exclude_none=True),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=response_cls,
            stream=stream,
            stream_cls=AsyncStream[response_cls],
        )


class ArkActionClient(Client, AsyncArk):
    def __init__(
        self,
        *,
        ak: str | None = None,
        sk: str | None = None,
        api_key: str | None = None,
        base_url: str | URL = BASE_URL,
        timeout: float | Timeout | None = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: AsyncClient | None = None,
        auto_refresh_apikey: bool = True,
    ) -> None:
        super().__init__(
            ak=ak,
            sk=sk,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        self.authorization = None
        # we only refresh api key when it is not set
        if auto_refresh_apikey and not self.api_key:
            self.authorization = ArkAuthorization(ak=ak, sk=sk)

        self.api_info = self.get_api_info()
        self.tool = AsyncTool(self)

    def _validate(self) -> None:
        if self.api_key is None and (self.sk is None or self.sk is None):
            raise AuthenticationError()

    def authorize(
        self,
        action_name: str,
        model: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        self._validate()

        if self.authorization:
            if model:
                self.api_key = self.authorization.get_apikey(
                    resource_ids=[model], resource_type="endpoint"
                )
            else:
                self.api_key = self.authorization.get_apikey(
                    resource_ids=[action_name], resource_type="action"
                )

        if not extra_headers:
            extra_headers = {}
        extra_headers["Authorization"] = f"Bearer {self.api_key}"
        extra_headers = get_extra_headers(extra_headers)
        return extra_headers

    @staticmethod
    def get_api_info() -> Dict[str, ApiInfo]:
        return {
            "Search": ApiInfo("POST", "/actions/Search", {}, {}, {}),
            "SearchIntention": ApiInfo(
                "POST", "/actions/SearchIntention/chat/completions", {}, {}, {}
            ),
            "SearchSummary": ApiInfo(
                "POST", "/actions/SearchSummary/chat/completions", {}, {}, {}
            ),
            "Calculator": ApiInfo("POST", "/actions/Calculator", {}, {}, {}),
            "LinkReader": ApiInfo("POST", "/actions/LinkReader", {}, {}, {}),
            "ActionTool": ApiInfo("POST", "/tools/execute", {}, {}, {}),
        }

    async def arequest(
        self,
        api: str,
        meta_info: Union[ArkActionMeta, ArkToolMeta],
        request: RequestType,
        response_cls: Type[ResponseType],
        extra_headers: Dict[str, str] | None = None,
        extra_query: Dict[str, object] | None = None,
        extra_body: Dict[str, object] | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> ResponseType:
        await self.init(meta_info)
        api_info = self.api_info.get(api)
        if not api_info:
            raise InvalidParameter("api")

        extra_headers = self.authorize(
            meta_info.action_name, meta_info.model, extra_headers
        )

        response = await self.tool.create(
            api_info.path,
            stream=False,
            request=request,
            response_cls=response_cls,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return response_cls.model_validate(response, strict=False)

    async def astream_request(
        self,
        api: str,
        meta_info: Union[ArkActionMeta, ArkToolMeta],
        request: RequestType,
        response_cls: Type[ResponseType],
        extra_headers: Dict[str, str] | None = None,
        extra_query: Dict[str, object] | None = None,
        extra_body: Dict[str, object] | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> AsyncIterable[ResponseType]:
        api_info = self.api_info.get(api)
        if not api_info:
            raise InvalidParameter("api")

        extra_headers = self.authorize(
            meta_info.action_name, meta_info.model, extra_headers
        )

        response: AsyncStream[Dict[str, Any]] = await self.tool.create(
            api_info.path,
            stream=True,
            request=request,
            response_cls=response_cls,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        async for resp in response:
            yield response_cls.model_validate(resp, strict=False)

    async def init(self, meta_info: Union[ArkActionMeta, ArkToolMeta]) -> None:
        await self.tool.init(meta_info=meta_info)
