import json
import os
import warnings
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Tuple

import aiohttp
from volcengine.ApiInfo import ApiInfo
from volcengine.base.Request import Request
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.maas.sse_decoder import SSEDecoder
from volcengine.maas.utils import dict_to_object
from volcengine.maas.v2.MaasService import (
    MaasException,
    new_client_sdk_request_error,
)
from volcengine.maas.v2.utils import gen_req_id
from volcengine.ServiceInfo import ServiceInfo

from ark.core.client import APIGAuthorization, AsyncSSEDecoder, Client
from ark.core.idl.maas_protocol import (
    MaasChatResponse,
)
from ark.core.utils.errors import InvalidParameter, MissingParameter


class AssistantClient(Client, Service):
    def __init__(
        self,
        host: str,
        region: str = "cn-beijing",
        api_path: str = "/api/v2/assistant/chat",
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        connection_timeout: float = 60,
        socket_timeout: float = 60,
        jwt_token: Optional[str] = None,
        auto_refresh_apikey: bool = True,
        service_id: Optional[str] = None,
    ):
        if service_id and region:
            self.service_id, region = service_id, region
        elif auto_refresh_apikey:
            self.service_id, region = self.parse_apig_host(host)

        service_info = self.get_service_info(
            host, region, connection_timeout, socket_timeout
        )
        api_info = self._get_api_info(api_path)
        super(AssistantClient, self).__init__(
            service_info=service_info, api_info=api_info
        )

        try:
            self.async_session: Optional[
                aiohttp.ClientSession
            ] = aiohttp.ClientSession()
        except Exception as e:
            self.async_session = None
            warnings.warn(str(e))

        self.set_ak(ak or os.getenv("VOLC_ACCESSKEY"))
        self.set_sk(sk or os.getenv("VOLC_SECRETKEY"))

        self._setted_apikey = jwt_token
        self.authorization = None
        if auto_refresh_apikey:
            self.authorization = APIGAuthorization(
                ak=self.service_info.credentials.ak,
                sk=self.service_info.credentials.sk,
            )

    @staticmethod
    def get_service_info(
        host: str, region: str, connection_timeout: float, socket_timeout: float
    ) -> ServiceInfo:
        service_info = ServiceInfo(
            host,
            {"Accept": "application/json"},
            Credentials("", "", "ark", region),
            connection_timeout,
            socket_timeout,
            "https",
        )
        return service_info

    @staticmethod
    def _get_api_info(api_path: str) -> Dict[str, ApiInfo]:
        api_info = {
            "chat": ApiInfo("POST", api_path, {}, {}, {}),
        }
        return api_info

    @staticmethod
    def parse_apig_host(host: str) -> Tuple[str, str]:
        if not isinstance(host, str):
            raise InvalidParameter("host")

        import re

        pattern = r"([\w.-]+)\.apigateway-([\w.-])+\.volceapi\.com.*"

        matches = re.match(pattern, host)

        if matches and len(matches.group()) >= 2:
            matched_groups = matches.groups()
            service_id, region = matched_groups[0], matched_groups[1]
            return service_id, region
        else:
            raise MissingParameter("service_id and region")

    def _validate(self, api: str, req_id: str) -> None:
        if self.authorization is None and self._setted_apikey is None:
            raise new_client_sdk_request_error("no valid credential", req_id)

        if api not in self.api_info:
            raise new_client_sdk_request_error("no such api", req_id)

    def set_apikey(self, apikey: str) -> None:
        self._setted_apikey = apikey

    def chat(self, req: Dict[str, Any]) -> MaasChatResponse:
        if self.authorization:
            self.set_apikey(self.authorization.get_apikey(service_id=self.service_id))

        req["stream"] = False
        return self._request("chat", req)

    async def achat(self, req: Dict[str, Any]) -> MaasChatResponse:
        if self.authorization:
            self.set_apikey(self.authorization.get_apikey(service_id=self.service_id))

        req["stream"] = False
        return await self._arequest("chat", req)

    def stream_chat(self, req: Dict[str, Any]) -> Iterator[MaasChatResponse]:
        req_id = gen_req_id()
        self._validate("chat", req_id)

        if self.authorization:
            self.set_apikey(self.authorization.get_apikey(service_id=self.service_id))

        assert self._setted_apikey, MissingParameter(
            "please check your ak/sk or jwttoken"
        )

        try:
            req["stream"] = True
            res = self._call(
                "chat",
                req_id,
                {},
                json.dumps(req),
                self._setted_apikey,
                stream=True,
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
                        if res.error is not None and res.error.code_n != 0:
                            raise MaasException(
                                res.error.code_n,
                                res.error.code,
                                res.error.message,
                                req_id,
                            )
                        yield res

            return iter()
        except MaasException:
            raise
        except Exception as e:
            raise new_client_sdk_request_error(str(e))

    async def async_stream_chat(
        self, req: Dict[str, Any]
    ) -> AsyncIterator[MaasChatResponse]:
        req_id = gen_req_id()
        self._validate("chat", req_id)

        if self.authorization:
            self.set_apikey(self.authorization.get_apikey(service_id=self.service_id))

        assert self._setted_apikey, MissingParameter(
            "please check your ak/sk or jwttoken"
        )

        req["stream"] = True
        try:
            res = await self._acall(
                "chat", req_id, {}, json.dumps(req), self._setted_apikey
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
                        if res.error is not None and res.error.code_n != 0:
                            raise MaasException(
                                res.error.code_n,
                                res.error.code,
                                res.error.message,
                                req_id,
                            )
                        yield res

            return iter()
        except Exception as e:
            raise e

    async def _arequest(
        self, api: str, req: Dict[str, Any], params: Dict[str, Any] = {}
    ) -> MaasChatResponse:
        req_id = gen_req_id()
        self._validate(api, req_id)

        if self.authorization:
            self.set_apikey(self.authorization.get_apikey(service_id=self.service_id))

        assert self._setted_apikey, MissingParameter(
            "please check your ak/sk or jwttoken"
        )

        try:
            res = await self._acall(
                api, req_id, params, json.dumps(req), self._setted_apikey
            )
            resp = dict_to_object(await res.json())
            if resp and isinstance(resp, dict):
                resp["req_id"] = req_id
            return resp
        except MaasException:
            raise
        except Exception as e:
            raise new_client_sdk_request_error(str(e), req_id)

    async def _acall(
        self, api: str, req_id: str, params: Dict[str, Any], body: str, apikey: str
    ) -> aiohttp.ClientResponse:
        assert self.async_session, ValueError("no async session")

        r = self._build_request(api, req_id, params, body, apikey)

        url = r.build()

        res = await self.async_session.post(
            url=url,
            headers=r.headers,
            data=r.body,
            timeout=aiohttp.ClientTimeout(
                sock_read=self.service_info.socket_timeout,
                connect=self.service_info.connection_timeout,
            ),
        )

        if res.status != 200:
            raw = await res.text()
            self._handle_exeption(raw, req_id)

        return res

    def _request(
        self, api: str, req: Dict[str, Any], params: Dict[str, Any] = {}
    ) -> MaasChatResponse:
        req_id = gen_req_id()

        self._validate(api, req_id)

        if self.authorization:
            self.set_apikey(self.authorization.get_apikey(service_id=self.service_id))

        assert self._setted_apikey, MissingParameter(
            "please check your ak/sk or jwttoken"
        )

        try:
            res = self._call(api, req_id, params, json.dumps(req), self._setted_apikey)
            resp = dict_to_object(res.json())
            if resp and isinstance(resp, dict):
                resp["req_id"] = req_id
            return resp

        except MaasException as e:
            raise e
        except Exception as e:
            raise new_client_sdk_request_error(str(e), req_id)

    def _call(
        self,
        api: str,
        req_id: str,
        params: Dict[str, Any],
        body: str,
        apikey: str,
        stream: bool = False,
    ) -> Request:
        r = self._build_request(api, req_id, params, body, apikey)

        url = r.build()
        res = self.session.post(
            url,
            headers=r.headers,
            data=r.body,
            timeout=(
                self.service_info.connection_timeout,
                self.service_info.socket_timeout,
            ),
            stream=stream,
        )

        if res.status_code != 200:
            raw = res.text.encode()
            res.close()
            self._handle_exeption(raw, req_id)

        return res

    def _handle_exeption(self, raw: str, req_id: str) -> None:
        try:
            resp = MaasChatResponse.model_validate_json(raw)
            resp.req_id = req_id
        except Exception:
            raise new_client_sdk_request_error(raw, req_id)
        else:
            if resp.error:
                raise MaasException(
                    resp.error.code_n, resp.error.code, resp.error.message, req_id
                )
            else:
                raise new_client_sdk_request_error(resp, req_id)

    def _build_request(
        self, api: str, req_id: str, params: Dict[str, Any], body: str, apikey: str
    ) -> Request:
        api_info = self.api_info[api]

        r = self.prepare_request(api_info, params)
        r.headers["X-Client-Request-Id"] = req_id
        r.headers["Content-Type"] = "application/json"
        r.body = body
        r.headers["Authorization"] = "Bearer " + apikey
        return r

    async def close_async_session(self) -> None:
        assert self.async_session, ValueError("no async session")
        return await self.async_session.close()
