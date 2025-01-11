import asyncio
from typing import Any, Dict, List, Optional, Union

import aiohttp
import requests

from ark.component.action.function_call import FunctionCall
from ark.component.action.utils import convert_actions, get_ark_client
from ark.core.client import ArkClient
from ark.core.idl.common_protocol import Action, ApiCall, Parameters
from ark.core.idl.maas_protocol import (
    MaasChatMessage,
)
from ark.core.task import task


class ActionCall(FunctionCall):
    actions: Dict[str, Action]
    api_credentials: Optional[Any] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        endpoint_id: str,
        messages: List[MaasChatMessage],
        actions: List[Dict[str, Any]],
        parameters: Optional[Union[Parameters, Dict[str, Any]]] = None,
        client: Optional[ArkClient] = None,
        api_credentials: Optional[Any] = None,
        extra: Optional[Dict[str, str]] = {},
        **kwargs: Any,
    ):
        converted_actions = convert_actions(actions)
        super().__init__(
            endpoint_id=endpoint_id,
            messages=messages,
            parameters=parameters,
            functions=[
                action.tool.function
                for action in converted_actions.values()
                if action.tool.function
            ],
            actions=converted_actions,  # type: ignore
            client=client or get_ark_client(),
            extra=extra,
            **kwargs,
        )
        self.api_credentials = api_credentials

    @task()
    async def async_call_apis(
        self, api_calls: Optional[List[ApiCall]] = None
    ) -> List[Any]:
        if api_calls is None or len(api_calls) == 0:
            return []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for api_call in api_calls:
                if api_call.name not in self.actions:
                    continue

                action = self.actions[api_call.name]
                tasks.append(
                    self._async_call_api(
                        session,
                        action.server.url,
                        action.path,
                        action.http_method,
                        api_call.headers,
                        api_call.parameters,
                        api_call.json_datas,
                    )
                )

            responses = await asyncio.gather(*tasks)
        return responses

    @staticmethod
    async def _async_call_api(
        session: aiohttp.ClientSession,
        base_url: str,
        path: str,
        method: str,
        headers: Optional[Any] = None,
        params: Optional[Any] = None,
        json_data: Optional[Any] = None,
    ) -> Any:
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        async with session.request(
            method=method, url=url, headers=headers, params=params, json=json_data
        ) as response:
            return await response.json()

    @task()
    async def call_apis(self, api_calls: Optional[List[ApiCall]] = None) -> List[Any]:
        if api_calls is None or len(api_calls) == 0:
            return []

        responses = []
        with requests.session() as session:
            for api_call in api_calls:
                if api_call.name not in self.actions:
                    continue

                action = self.actions[api_call.name]
                response = self._call_api(
                    session,
                    action.server.url,
                    action.path,
                    action.http_method,
                    api_call.headers,
                    api_call.parameters,
                    api_call.json_datas,
                )
                responses.append(response)
        return responses

    @staticmethod
    def _call_api(
        session: requests.Session,
        base_url: str,
        path: str,
        method: str,
        headers: Optional[Any] = None,
        params: Optional[Any] = None,
        json_data: Optional[Any] = None,
    ) -> Any:
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        return session.request(
            method, url, headers=headers, params=params, json=json_data
        )
