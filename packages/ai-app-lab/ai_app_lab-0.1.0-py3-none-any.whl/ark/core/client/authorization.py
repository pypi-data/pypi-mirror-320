import json
import os
import time
from typing import Any, Dict, List, Optional, Set, Union

from volcengine.ApiInfo import ApiInfo
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.maas.exception import MaasException, new_client_sdk_request_error
from volcengine.ServiceInfo import ServiceInfo

from ark.core.client.base import Client


class ArkAuthorization(Client, Service):
    def __init__(
        self,
        host: str = "open.volcengineapi.com",
        region: str = "cn-beijing",
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        connection_timeout: int = 300,
        socket_timeout: int = 300,
        **kwargs: Any,
    ):
        ak = ak or os.getenv("VOLC_ACCESSKEY")
        sk = sk or os.getenv("VOLC_SECRETKEY")
        service_info: ServiceInfo = self.get_service_info(
            host, region, ak, sk, connection_timeout, socket_timeout
        )
        api_info: Dict[str, ApiInfo] = self.get_api_info()

        super().__init__(service_info=service_info, api_info=api_info, **kwargs)
        self.resource_ids: Set[str] = set()
        self._setted_apikey: Optional[str] = None
        self._apikey_ttl: int = 604800

        self.set_ak(ak)
        self.set_sk(sk)

    @staticmethod
    def get_service_info(
        host: str,
        region: str,
        ak: Optional[str],
        sk: Optional[str],
        connection_timeout: int,
        socket_timeout: int,
    ) -> ServiceInfo:
        service_info = ServiceInfo(
            host,
            {"Accept": "application/json"},
            Credentials(ak, sk, "ark", region),
            connection_timeout,
            socket_timeout,
            "https",
        )
        return service_info

    @staticmethod
    def get_api_info() -> Dict[str, ApiInfo]:
        api_info = {
            "get_apikey": ApiInfo(
                method="POST",
                path="/",
                query={"Action": "GetApiKey", "Version": "2024-01-01"},
                form={},
                header={},
            )
        }
        return api_info

    def get_apikey_ttl(self) -> int:
        return self._apikey_ttl

    def _set_apikey_ttl(self, ttl: int) -> None:
        self._apikey_ttl = ttl

    def generate_apikey(
        self,
        resource_ids: List[str],
        ttl: int = 604800,
        resource_type: str = "endpoint",
    ) -> str:
        assert len(resource_ids) > 0

        req = {
            "DurationSeconds": ttl,
            "ResourceType": resource_type,
            "ResourceIds": resource_ids,
        }
        try:
            res = self.json("get_apikey", {}, json.dumps(req))
            res = json.loads(res)
            apikey = res.get("Result", {}).get("ApiKey", "")
            self._setted_apikey = apikey

            self._set_apikey_ttl(ttl + int(time.time()))
            return apikey
        except MaasException as e:
            raise e
        except Exception as e:
            raise new_client_sdk_request_error(str(e))

    def get_invalid_resource_ids(
        self, resource_ids: Union[Set[str], List[str]]
    ) -> List[str]:
        resource_ids_set = set(resource_ids)
        invalid_resource_ids = resource_ids_set - self.resource_ids

        return list(invalid_resource_ids)

    def get_apikey(
        self,
        resource_ids: Union[List[str], Set[str]],
        ttl: int = 604800,
        resource_type: str = "endpoint",
    ) -> Optional[str]:
        # exists invalid resource id
        if (
            self._setted_apikey is None
            or len(self.get_invalid_resource_ids(resource_ids)) > 0
        ):
            self.generate_apikey(list(resource_ids), ttl, resource_type)
            self.resource_ids = set(resource_ids)

        # 过期5分钟前,重新生成
        if time.time() + 300 > self.get_apikey_ttl():
            self.generate_apikey(list(resource_ids), ttl, resource_type)
            self.resource_ids = set(resource_ids)

        return self._setted_apikey


class APIGAuthorization(Client, Service):
    def __init__(
        self,
        host: str = "open.volcengineapi.com",
        region: str = "cn-beijing",
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        connection_timeout: int = 300,
        socket_timeout: int = 300,
        **kwargs: Any,
    ) -> None:
        ak = ak or os.getenv("VOLC_ACCESSKEY")
        sk = sk or os.getenv("VOLC_SECRETKEY")
        service_info = self.get_service_info(
            host, region, ak, sk, connection_timeout, socket_timeout
        )
        api_info = self.get_api_info()

        super().__init__(service_info=service_info, api_info=api_info, **kwargs)
        self._setted_apikey: Optional[str] = None
        self._apikey_ttl: int = 604800

        self.set_ak(ak)
        self.set_sk(sk)

    @staticmethod
    def get_service_info(
        host: str,
        region: str,
        ak: Optional[str],
        sk: Optional[str],
        connection_timeout: int,
        socket_timeout: int,
    ) -> ServiceInfo:
        service_info = ServiceInfo(
            host,
            {"Accept": "application/json"},
            Credentials(ak, sk, "apig", region),
            connection_timeout,
            socket_timeout,
            "https",
        )
        return service_info

    @staticmethod
    def get_api_info() -> Dict[str, ApiInfo]:
        api_info = {
            "get_jwttoken": ApiInfo(
                method="POST",
                path="/",
                query={"Action": "GetJwtToken", "Version": "2021-03-03"},
                form={},
                header={},
            )
        }
        return api_info

    def get_apikey_ttl(self) -> int:
        return self._apikey_ttl

    def _set_apikey_ttl(self, ttl: int) -> None:
        self._apikey_ttl = ttl

    def generate_apikey(
        self, service_id: Optional[str] = None, gateway_id: Optional[str] = None
    ) -> str:
        ttl: int = 604800
        req = {"GatewayId": gateway_id, "ServiceId": service_id}
        try:
            res = self.json("get_jwttoken", {}, json.dumps(req))
            res = json.loads(res)

            apikey = res.get("Result", {}).get("JwtToken", "")
            self._setted_apikey = apikey
            self._set_apikey_ttl(ttl + int(time.time()))

            return apikey
        except MaasException as e:
            raise e
        except Exception as e:
            raise new_client_sdk_request_error(str(e))

    def get_apikey(
        self, service_id: Optional[str] = None, gateway_id: Optional[str] = None
    ) -> str:
        assert (
            gateway_id or service_id
        ), "either gateway_id or service_id should be filled"

        if self._setted_apikey is None:
            return self.generate_apikey(service_id, gateway_id)

        if time.time() + 300 > self.get_apikey_ttl():  # 过期5分钟前,重新生成
            return self.generate_apikey(service_id, gateway_id)

        return self._setted_apikey
