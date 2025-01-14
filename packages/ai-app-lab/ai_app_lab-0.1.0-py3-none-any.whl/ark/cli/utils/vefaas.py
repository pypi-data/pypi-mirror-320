import json
import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from volcengine.ApiInfo import ApiInfo
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

from ark.core.client.base import Client


class InvalidOperationError(Exception):
    def __init__(
        self, message: str, code: str = "InvalidOperation", data: dict = {}
    ) -> None:
        self.code = code
        self.message = message
        self.data = data

    def is_invalid_image_status(self) -> bool:
        return "Source image sync is in Running status" in self.message


class Env(BaseModel):
    Key: str
    Value: str


class Item(BaseModel):
    Key: str
    Value: List[str]


class Filter(BaseModel):
    Item: Item


class Function(BaseModel):
    Id: str
    Name: str
    Description: Optional[str] = None
    Runtime: str
    ExclusiveMode: bool
    RequestTimeout: int
    MaxReplicas: Optional[int] = None
    MaxConcurrency: int
    MemoryMB: int
    Envs: Optional[List[Env]] = None
    CreationTime: str
    LastUpdateTime: str


class ReleaseFunctionResponse(BaseModel):
    FunctionId: str
    Status: str
    StatusMessage: Optional[str] = None
    StableRevisionNumber: Optional[int] = None
    ErrorCode: Optional[str] = None


class VeFaaS(Client, Service):
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
        super().__init__(
            service_info=self.get_service_info(
                host, region, connection_timeout, socket_timeout
            ),
            api_info=self.get_api_info(),
            **kwargs,
        )
        self.set_ak(ak or os.getenv("VOLC_ACCESSKEY"))
        self.set_sk(sk or os.getenv("VOLC_SECRETKEY"))

    @staticmethod
    def get_service_info(
        host: str,
        region: str,
        connection_timeout: int,
        socket_timeout: int,
    ) -> ServiceInfo:
        service_info = ServiceInfo(
            host,
            {"Accept": "application/json"},
            Credentials("", "", "vefaas", region),
            connection_timeout,
            socket_timeout,
            "https",
        )
        return service_info

    @staticmethod
    def get_api_info() -> Dict[str, ApiInfo]:
        api_info = {
            "ListFunctions": ApiInfo(
                "POST",
                "/ListFunctions",
                {"Action": "ListFunctions", "Version": "2021-03-03"},
                {},
                {},
            ),
            "Release": ApiInfo(
                "POST",
                "/Release",
                {"Action": "Release", "Version": "2021-03-03"},
                {},
                {},
            ),
            "CreateFunction": ApiInfo(
                "POST",
                "/CreateFunction",
                {"Action": "CreateFunction", "Version": "2021-03-03"},
                {},
                {},
            ),
            "UpdateFunction": ApiInfo(
                "POST",
                "/UpdateFunction",
                {"Action": "UpdateFunction", "Version": "2021-03-03"},
                {},
                {},
            ),
            "CreateApigTrigger": ApiInfo(
                "POST",
                "/CreateApigTrigger",
                {"Action": "CreateApigTrigger", "Version": "2021-03-03"},
                {},
                {},
            ),
        }
        return api_info

    def get_function_by_name(self, name: str) -> Function:
        try:
            item = Item(Key="Name", Value=[name])
            filter = Filter(Item=item).model_dump()
            req = {
                "Filters": [filter],
            }
            res = self.json("ListFunctions", {}, json.dumps(req))
            res = json.loads(res)
            functions = res.get("Result", {}).get("Items", [])
            assert len(functions) > 0, "No function found"
            return Function.model_validate(functions[0])
        except Exception:
            raise

    def update_function_image(self, function_id: str, source: str) -> Function:
        try:
            req = {"Id": function_id, "SourceType": "image", "Source": source}
            res = self.json("UpdateFunction", {}, json.dumps(req))
            res = json.loads(res)
            function = res.get("Result", {})

            return Function.model_validate(function)
        except Exception:
            raise

    def release_function(  # type: ignore
        self,
        function_name: str,
        function_id: Optional[str] = None,
        revision_number: int = 0,
    ) -> ReleaseFunctionResponse:
        try:
            req = {
                "FunctionId": function_id
                or self.get_function_by_name(function_name).Id,
                "RevisionNumber": revision_number,
            }
            res = self.json("Release", {}, json.dumps(req))
            res = json.loads(res)
            resp = res.get("Result", {})

            return ReleaseFunctionResponse.model_validate(resp)
        except Exception as e:
            resp_err = json.loads(e.args[0])
            error = resp_err.get("ResponseMetadata", {}).get("Error", {})
            if error.get("Code", "") == "InvalidOperation":
                raise InvalidOperationError(error.get("Message", ""))
