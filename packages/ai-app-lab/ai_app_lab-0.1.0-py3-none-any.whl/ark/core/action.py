import asyncio
import time
from typing import Any, Generic, Optional, Tuple, Type, Union

from httpx import Timeout
from pydantic import BaseModel, Field
from volcenginesdkarkruntime._exceptions import (
    ArkAPIError,
)

from ark.core.client import ArkActionClient, Client, get_client_pool
from ark.core.idl.ark_protocol import ArkActionMeta
from ark.core.idl.common_protocol import (
    ActionDetails,
    ExceptionInfo,
    RequestType,
    ResponseType,
    ToolDetails,
    ToolOutput,
    ToolOutputType,
)
from ark.core.task.task import task
from ark.core.utils.errorsv3 import (
    FALLBACK_EXCEPTIONS,
    APIException,
    APITimeoutError,
    InternalServiceError,
)


def _get_ark_client() -> Optional[Client]:
    client_pool = get_client_pool()
    client = client_pool.get_client("action")
    if not client:
        client = ArkActionClient(timeout=Timeout(connect=1.0, timeout=60.0))
    return client


def _ns_to_ms(ns: int) -> int:
    return int(ns / 1e6)


class Action(BaseModel, Generic[RequestType, ResponseType]):
    client: ArkActionClient = Field(default_factory=_get_ark_client)
    name: str
    meta_info: ArkActionMeta = Field(default_factory=ArkActionMeta)
    response_cls: Type[ResponseType]

    class Config:
        arbitrary_types_allowed = True

    def run(self, request: RequestType, **kwargs: Any) -> ResponseType:
        raise NotImplementedError

    @task(watch_io=False)
    async def arun(
        self, request: RequestType, **kwargs: Any
    ) -> Union[ResponseType, Tuple[ResponseType, ActionDetails]]:
        created_at = _ns_to_ms(time.time_ns())
        exception: Optional[Exception] = None
        try:
            response = await self.client.arequest(
                api=self.name,
                meta_info=self.meta_info,
                request=request,
                response_cls=self.response_cls,
                extra_headers=kwargs.get("extra_headers"),
                extra_query=kwargs.get("extra_query"),
                extra_body=kwargs.get("extra_body"),
                timeout=kwargs.get("timeout"),
            )
        except Exception as e:
            if isinstance(e, asyncio.TimeoutError):
                exception = APITimeoutError(str(e))
            else:
                exception = e
        finally:
            completed_at = _ns_to_ms(time.time_ns())

        if "include_details" in kwargs and kwargs["include_details"] is True:
            action_details = ActionDetails(
                name=self.meta_info.action_name
                if self.meta_info.action_name
                else self.name,
                count=1,
                tool_details=[
                    ToolDetails(
                        name=self.name,
                        input=request.model_dump(exclude_unset=True, exclude_none=True),
                        output=response.model_dump(
                            exclude_unset=True, exclude_none=True
                        )
                        if exception is None
                        else ToolOutput(
                            type=ToolOutputType.EXCEPTION,
                            data=ExceptionInfo(
                                type=exception.__class__.__name__,
                                message=exception.message
                                if isinstance(exception, (ArkAPIError, APIException))
                                else InternalServiceError(str(exception)).message,
                            ),
                        ),
                        created_at=created_at,
                        completed_at=completed_at,
                    )
                ],
            )
            if exception is not None and hasattr(exception, "message"):
                exception.message = action_details.model_dump_json(exclude_none=True)

        if exception is not None:
            if kwargs.get("special_exception_fallback") and (
                isinstance(exception, FALLBACK_EXCEPTIONS)
            ):
                response = self.response_cls()
            else:
                raise exception

        if "include_details" in kwargs and kwargs["include_details"] is True:
            return response, action_details
        return response
