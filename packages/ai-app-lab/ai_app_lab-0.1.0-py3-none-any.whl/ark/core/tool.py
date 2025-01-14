import asyncio
import time
from typing import Any, AsyncIterable, Dict, Optional, Tuple, Union

from pydantic import BaseModel, Field
from volcenginesdkarkruntime._exceptions import (
    ArkAPIError,
)

from ark.core.client import ArkActionClient, Client, get_client_pool
from ark.core.idl.ark_protocol import (
    ArkToolMeta,
    ArkToolRequest,
    ArkToolResponse,
)
from ark.core.idl.common_protocol import (
    ActionDetails,
    ExceptionInfo,
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


def _get_tool_client() -> Optional[Client]:
    client_pool = get_client_pool()
    client = client_pool.get_client("action")
    if not client:
        client = ArkActionClient()
    return client


def _ns_to_ms(ns: int) -> int:
    return int(ns / 1e6)


class ActionTool(BaseModel):
    client: ArkActionClient = Field(default_factory=_get_tool_client)
    meta_info: ArkToolMeta = Field(default_factory=ArkToolMeta)

    class Config:
        arbitrary_types_allowed = True

    async def get_schema(self) -> Dict[str, Any]:
        return {}

    @task(watch_io=False)
    async def arun(
        self,
        request: Optional[Dict[str, Any]] = None,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> Union[ArkToolResponse, Tuple[ArkToolResponse, ActionDetails]]:
        created_at = _ns_to_ms(time.time_ns())
        exception: Optional[Exception] = None
        try:
            request_data = ArkToolRequest(
                action_name=self.meta_info.action_name,
                tool_name=self.meta_info.tool_name,
                parameters=request,
                dry_run=dry_run,
                timeout=(kwargs or {}).get("timeout", 60),
            )

            response = await self.client.arequest(
                api=self.__class__.__name__,
                meta_info=self.meta_info,
                request=request_data,
                response_cls=ArkToolResponse,
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
                name=self.meta_info.action_name,
                count=1,
                tool_details=[
                    ToolDetails(
                        name=self.meta_info.tool_name,
                        input=request,
                        output=(
                            ToolOutput(
                                type=ToolOutputType.TOOL,
                                data=response.model_dump(
                                    exclude_unset=True, exclude_none=True
                                ),
                            )
                            if exception is None
                            else ToolOutput(
                                type=ToolOutputType.EXCEPTION,
                                data=ExceptionInfo(
                                    type=exception.__class__.__name__,
                                    message=(
                                        exception.message
                                        if isinstance(
                                            exception, (ArkAPIError, APIException)
                                        )
                                        else InternalServiceError(
                                            str(exception)
                                        ).message
                                    ),
                                ),
                            )
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
                response = ArkToolResponse()
            else:
                raise exception

        if "include_details" in kwargs and kwargs["include_details"] is True:
            return response, action_details
        return response

    @task()
    async def acall(
        self, request: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Union[ArkToolResponse, AsyncIterable[ArkToolResponse]]:
        """
        for ActionTool acall
        """
        return await self.arun(request, **kwargs)
