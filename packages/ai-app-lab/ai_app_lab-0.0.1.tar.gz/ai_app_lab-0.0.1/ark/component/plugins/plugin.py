from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from pydantic import BaseModel, Field, field_validator
from typing_extensions import Literal

from ark.core._api.deprecation import deprecated
from ark.core.client import ArkClient, Client, get_client_pool
from ark.core.idl.common_protocol import ChatRole, Parameters, Tool
from ark.core.idl.maas_protocol import (
    MaasChatMessage,
    MaasChatRequest,
    MaasChatResponse,
)
from ark.core.task import task


def _get_ark_client() -> Optional[Client]:
    client_pool = get_client_pool()
    client = client_pool.get_client("chat")
    if not client:
        client = ArkClient()
    return client


def convert_messages_to_keywords(messages: List[MaasChatMessage]) -> List[str]:
    keywords: List[str] = []
    for message in messages:
        if message.role == ChatRole.SYSTEM:
            continue
        if message.role == ChatRole.FUNCTION:
            continue
        if not isinstance(message.content, str):
            continue
        keywords.append(message.content)
    return keywords


@deprecated(
    since="0.1.11", removal="0.2.0", alternative_import="ark.core.action.Action"
)
class Plugin(BaseModel):
    name: Literal["SearchIntention", "SearchSummary"]
    endpoint_id: str
    messages: List[MaasChatMessage] = Field(default_factory=list)
    parameters: Optional[Union[Parameters, Dict[str, Any]]] = None
    options: Optional[Dict[str, Any]] = None
    client: ArkClient = Field(default_factory=_get_ark_client)
    _tools: Optional[List[Tool]] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    async def arun(self) -> MaasChatResponse:
        request = MaasChatRequest(
            messages=self.messages,
            tools=self._tools,
            parameters=self.parameters,
        )

        return await self._arun(self.endpoint_id, request)

    async def astream(self) -> AsyncIterator[MaasChatResponse]:
        request = MaasChatRequest(
            stream=True,
            messages=self.messages,
            tools=self._tools,
            parameters=self.parameters,
        )
        responses = await self._arun(self.endpoint_id, request)

        async for resp in responses:
            yield resp

    def run(self) -> MaasChatResponse:
        request = MaasChatRequest(
            messages=self.messages,
            tools=self._tools,
            parameters=self.parameters,
        )
        return self._run(self.endpoint_id, request)

    def stream(self) -> Iterator[MaasChatResponse]:
        request = MaasChatRequest(
            stream=True,
            messages=self.messages,
            tools=self._tools,
            parameters=self.parameters,
        )

        for resp in self._run(self.endpoint_id, request):
            yield resp

    @task()
    async def _arun(
        self, endpoint_id: str, request: MaasChatRequest
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

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: List[MaasChatMessage]) -> List[MaasChatMessage]:
        if not v or len(v) == 0:
            raise ValueError("Messages are required")

        pre_role = None  # user, assistant, function, system
        for msg in v:
            if not msg.role:
                raise ValueError("Role is required")
            if msg.content is None:
                msg.content = ""

            if msg.role == ChatRole.SYSTEM:
                continue

            if msg.role == ChatRole.USER:
                assert (
                    not pre_role or pre_role == ChatRole.ASSISTANT
                ), f"{pre_role} message should not followed by a user message"

            if msg.role == ChatRole.ASSISTANT:
                assert pre_role in [
                    ChatRole.USER,
                    ChatRole.FUNCTION,
                ], "Assistant message should follow a user or function message"

            if msg.role == ChatRole.FUNCTION:
                assert (
                    pre_role == ChatRole.ASSISTANT
                ), "Function message should follow an assistant message"

            pre_role = msg.role

        return v
