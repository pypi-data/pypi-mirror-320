from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from pydantic import BaseModel, Field

from ark.component.action.utils import ToolTypeFunction, get_ark_client
from ark.core.client import ArkClient
from ark.core.idl.common_protocol import Function, Parameters, Tool
from ark.core.idl.maas_protocol import (
    MaasChatMessage,
    MaasChatRequest,
    MaasChatResponse,
)
from ark.core.task import task


class FunctionCall(BaseModel):
    endpoint_id: str
    messages: List[MaasChatMessage]
    functions: List[Function]
    parameters: Optional[Union[Parameters, Dict[str, Any]]] = Field(
        default_factory=dict
    )
    client: ArkClient = Field(default_factory=get_ark_client)
    extra: Optional[Dict[str, str]] = Field(default_factory=dict)
    _tools: Optional[List[Tool]] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @property
    def tools(self) -> List[Tool]:
        if not self._tools:
            self._tools = [
                Tool(type=ToolTypeFunction, function=function)
                for function in self.functions
            ]
        return self._tools

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

    async def arun(self) -> MaasChatResponse:
        request = MaasChatRequest(
            messages=self.messages,
            tools=self.tools,
            parameters=self.parameters,
            extra=self.extra,
        )

        return await self._arun(self.endpoint_id, request)

    async def astream(self) -> AsyncIterator[MaasChatResponse]:
        request = MaasChatRequest(
            stream=True,
            messages=self.messages,
            tools=self.tools,
            parameters=self.parameters,
            extra=self.extra,
        )

        async for resp in await self._arun(self.endpoint_id, request):
            yield resp

    def run(self) -> MaasChatResponse:
        request = MaasChatRequest(
            messages=self.messages,
            tools=self.tools,
            parameters=self.parameters,
            extra=self.extra,
        )
        return self._run(self.endpoint_id, request)

    def stream(self) -> Iterator[dict]:
        request = MaasChatRequest(
            stream=True,
            messages=self.messages,
            tools=self.tools,
            parameters=self.parameters,
            extra=self.extra,
        )

        for resp in self._run(self.endpoint_id, request):
            yield resp
