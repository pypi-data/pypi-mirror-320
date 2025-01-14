import copy
import json
import os
import warnings
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Set, Type, Union

import aiohttp
from pydantic import BaseModel
from volcengine.ApiInfo import ApiInfo
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.maas.v2.MaasService import (
    MaasException,
    MaasService,
    SSEDecoder,
    gen_req_id,
    json_to_object,
    new_client_sdk_request_error,
)

from ark.core.client import Client
from ark.core.client.authorization import ArkAuthorization
from ark.core.client.sse import AsyncSSEDecoder
from ark.core.idl.maas_protocol import (
    MaasChatRequest,
    MaasChatResponse,
    MaasClassificationRequest,
    MaasClassificationResponse,
    MaasEmbeddingsRequest,
    MaasEmbeddingsResponse,
    MaasTokenizeRequest,
    MaasTokenizeResponse,
    SearchRequest,
    SearchResponse,
)
from ark.core.utils.context import get_extra_headers, get_reqid
from ark.core.utils.errors import (
    GPTException,
)


class ArkClient(Client, MaasService):
    def __init__(
        self,
        host: str = "maas-api.ml-platform-cn-beijing.volces.com",
        region: str = "cn-beijing",
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        connection_timeout: float = 60,
        socket_timeout: float = 60,
        apikey: Optional[str] = None,
        auto_refresh_apikey: bool = False,
        max_retries: int = 1,
        **kwargs: Any,
    ):
        super().__init__(
            host=host,
            region=region,
            connection_timeout=connection_timeout,
            socket_timeout=socket_timeout,
            **kwargs,
        )
        ak = ak or os.getenv("VOLC_ACCESSKEY")
        sk = sk or os.getenv("VOLC_SECRETKEY")
        self.set_ak(ak)
        self.set_sk(sk)

        self.add_action_info()

        self._setted_apikey: Optional[str] = None
        if apikey:
            self.set_apikey(apikey=apikey)

        self.authorization = None
        try:
            self.async_session: Optional[
                aiohttp.ClientSession
            ] = aiohttp.ClientSession()
        except Exception as e:
            self.async_session = None
            warnings.warn(str(e))

        if auto_refresh_apikey:
            self.endpoint_ids: Set[str] = set()
            self.authorization = ArkAuthorization(ak=ak, sk=sk)

        self.max_retries = max_retries

    def add_action_info(self) -> Dict[str, ApiInfo]:
        action_info = {
            "search": ApiInfo("POST", "/api/v2/action/Search", {}, {}, {}),
            "search_intention": ApiInfo(
                "POST", "/api/v2/action/SearchIntention", {}, {}, {}
            ),
            "search_summary": ApiInfo(
                "POST", "/api/v2/action/SearchSummary", {}, {}, {}
            ),
        }

        self.api_info.update(action_info)
        return self.api_info

    def set_apikey(
        self, endpoint_id: Optional[str] = None, apikey: Optional[str] = None
    ) -> None:
        if apikey:
            self._setted_apikey = apikey
            return

        if endpoint_id and self.authorization:
            self.endpoint_ids.add(endpoint_id)
            self._setted_apikey = self.authorization.get_apikey(
                resource_ids=self.endpoint_ids
            )

    def _validate(self, api: str, req_id: str) -> None:
        if self.service_info.credentials is None or (
            self._setted_apikey is None
            and (
                self.service_info.credentials.sk is None
                or self.service_info.credentials.ak is None
            )
        ):
            raise new_client_sdk_request_error("no valid credential", req_id)

        if api not in self.api_info:
            raise new_client_sdk_request_error("no such api", req_id)

    def chat(self, endpoint_id: str, req: Dict[str, Any]) -> MaasChatResponse:
        if self.authorization:
            self.set_apikey(endpoint_id=endpoint_id)

        req["stream"] = False
        return self._request(endpoint_id, "chat", req)

    def stream_chat(
        self, endpoint_id: str, req: Union[MaasChatRequest, Dict[str, Any]]
    ) -> Iterator[MaasChatResponse]:
        if self.authorization:
            self.set_apikey(endpoint_id=endpoint_id)

        req_id: str = get_reqid() or gen_req_id()
        self._validate("chat", req_id)
        try:
            if isinstance(req, MaasChatRequest):
                req.stream = True
                data: str = req.model_dump_json(exclude_unset=True, exclude_none=True)
            else:
                req["stream"] = True
                data = json.dumps(req)

            res = self._call(
                endpoint_id,
                "chat",
                req_id,
                {},
                data,
                self._setted_apikey,
            )
            decoder = SSEDecoder(res)

            def iter() -> Iterator[MaasChatResponse]:
                for data in decoder.next():
                    if data == b"[DONE]":
                        return

                    try:
                        res = MaasChatResponse.model_validate_json(
                            str(data, encoding="utf-8")
                        )
                        res.req_id = req_id
                    except:
                        raise
                    else:
                        if res.error:
                            if res.error and res.error.code_n:
                                raise GPTException(
                                    code_n=res.error.code_n,
                                    message=res.error.message,
                                )
                        yield res

            return iter()
        except MaasException:
            raise
        except Exception as e:
            raise new_client_sdk_request_error(str(e))

    async def async_stream_chat(
        self, endpoint_id: str, req: Union[MaasChatRequest, Dict[str, Any]]
    ) -> AsyncIterator[MaasChatResponse]:
        if self.authorization:
            self.set_apikey(endpoint_id=endpoint_id)

        req_id = get_reqid() or gen_req_id()
        self._validate("chat", req_id)

        if isinstance(req, MaasChatRequest):
            req.stream = True
            data = req.model_dump_json(exclude_unset=True, exclude_none=True)
        else:
            req["stream"] = True
            data = json.dumps(req)

        try:
            res = await self._acall(
                endpoint_id, "chat", req_id, {}, data, self._setted_apikey
            )
            decoder = AsyncSSEDecoder(res.content)

            async def iter() -> AsyncIterator[MaasChatResponse]:
                async for data in decoder.next():
                    if data == b"[DONE]":
                        return

                    try:
                        res = MaasChatResponse.model_validate_json(
                            str(data, encoding="utf-8")
                        )
                        res.req_id = req_id
                    except:
                        raise
                    else:
                        if res.error and res.error.code_n:
                            raise GPTException(
                                code_n=res.error.code_n,
                                message=res.error.message,
                            )
                        yield res

            return iter()
        except Exception as e:
            raise e

    def tokenize(self, endpoint_id: str, req: Dict[str, Any]) -> MaasTokenizeResponse:
        if self.authorization:
            self.set_apikey(endpoint_id=endpoint_id)

        return self._request(endpoint_id, "tokenization", req)

    def classification(
        self, endpoint_id: str, req: Dict[str, Any]
    ) -> MaasClassificationResponse:
        if self.authorization:
            self.set_apikey(endpoint_id=endpoint_id)
        return self._request(endpoint_id, "classification", req)

    def embeddings(
        self, endpoint_id: str, req: Dict[str, Any]
    ) -> MaasEmbeddingsResponse:
        if self.authorization:
            self.set_apikey(endpoint_id=endpoint_id)
        return self._request(endpoint_id, "embeddings", req)

    async def async_chat(
        self, endpoint_id: str, req: Union[MaasChatRequest, Dict[str, Any]]
    ) -> MaasChatResponse:
        if isinstance(req, MaasChatRequest):
            req.stream = False
        else:
            req["stream"] = False
        return await self._arequest(endpoint_id, "chat", req, cls=MaasChatResponse)

    async def async_tokenize(
        self, endpoint_id: str, req: Union[MaasTokenizeRequest, Dict[str, Any]]
    ) -> MaasTokenizeResponse:
        return await self._arequest(
            endpoint_id, "tokenization", req, cls=MaasTokenizeResponse
        )

    async def async_classification(
        self, endpoint_id: str, req: Union[MaasClassificationRequest, Dict[str, Any]]
    ) -> MaasClassificationResponse:
        return await self._arequest(
            endpoint_id, "classification", req, cls=MaasClassificationResponse
        )

    async def async_embeddings(
        self, endpoint_id: str, req: Union[MaasEmbeddingsRequest, Dict[str, Any]]
    ) -> MaasEmbeddingsResponse:
        return await self._arequest(
            endpoint_id, "embeddings", req, cls=MaasEmbeddingsResponse
        )

    async def async_search(
        self, endpoint_id: str, request: SearchRequest
    ) -> SearchResponse:
        return await self._arequest(endpoint_id, "search", request, cls=SearchResponse)

    async def _arequest(
        self,
        endpoint_id: str,
        api: str,
        req: Union[BaseModel, Dict[str, Any]],
        params: Dict[str, Any] = {},
        cls: Type[BaseModel] = MaasChatResponse,
    ) -> Any:
        req_id = get_reqid() or gen_req_id()
        if self.authorization:
            self.set_apikey(endpoint_id=endpoint_id)

        self._validate(api, req_id)

        try:
            data: str = (
                req.model_dump_json(exclude_unset=True, exclude_none=True)
                if isinstance(req, BaseModel)
                else json.dumps(req)
            )

            res = await self._acall(
                endpoint_id,
                api,
                req_id,
                params,
                data,
                self._setted_apikey,
            )

            resp = cls.model_validate(await res.json())
            if "req_id" in cls.model_fields:
                resp.req_id = req_id  # type: ignore
            return resp

        except (MaasException, GPTException):
            raise
        except Exception as e:
            raise new_client_sdk_request_error(str(e), req_id)

    async def _acall(
        self,
        endpoint_id: str,
        api: str,
        req_id: str,
        params: Dict[str, Any],
        body: str,
        apikey: Optional[str] = None,
    ) -> aiohttp.ClientResponse:
        r = self._build_request(endpoint_id, api, req_id, params, body, apikey)

        url = r.build()
        last_err = None
        for i in range(self.max_retries):
            try:
                if not self.async_session:
                    self.async_session = aiohttp.ClientSession()

                res = await self.async_session.post(
                    url=url,
                    headers=r.headers,
                    data=r.body,
                    timeout=aiohttp.ClientTimeout(
                        total=-1,
                        sock_read=self.service_info.socket_timeout,
                        connect=self.service_info.connection_timeout,
                    ),
                )
                if res.status != 200:
                    raw: Union[str, bytes] = await res.text()
                    try:
                        resp = json_to_object(
                            raw if isinstance(raw, str) else raw.decode("utf-8"),
                            req_id=req_id,
                        )  # type: ignore
                    except Exception:
                        raise new_client_sdk_request_error(raw, req_id)
                    else:
                        if resp.error:
                            raise GPTException(
                                code_n=resp.error.code_n, message=resp.error.message
                            )
                        else:
                            raise new_client_sdk_request_error(resp, req_id)
                return res
            except Exception as e:
                last_err = e

        if last_err:
            raise last_err
        else:
            raise new_client_sdk_request_error(
                f"retry {self.max_retries} times failed", req_id
            )

    def _build_request(
        self,
        endpoint_id: str,
        api: str,
        req_id: str,
        params: Dict[str, Any],
        body: str,
        apikey: Optional[str] = None,
    ) -> Request:
        api_info = copy.deepcopy(self.api_info[api])
        api_info.path = api_info.path.format(endpoint_id=endpoint_id)

        r = self.prepare_request(api_info, params)
        r.headers["x-tt-logid"] = req_id
        r.headers["Content-Type"] = "application/json"
        r.body = body

        if apikey is None:
            SignerV4.sign(r, self.service_info.credentials)
        elif apikey is not None:
            r.headers["Authorization"] = "Bearer " + apikey
        extra_headers = get_extra_headers()
        if extra_headers:
            r.headers.update(extra_headers)

        return r
