import json
import os
from typing import Any, Callable, Dict, Iterable, Optional, Tuple, Type

from fastapi import HTTPException
from volcenginesdkarkruntime import AsyncArk
from volcenginesdkarkruntime._constants import BASE_URL

from ark.core.client import Client, get_client_pool
from ark.core.client.action import ArkActionClient
from ark.core.client.maas import ArkClient
from ark.core.idl.common_protocol import Context, Request, RequestType, ResponseType
from ark.core.idl.maas_protocol import MaasChatRequest
from ark.core.launcher.vefaas.common import parse_request
from ark.core.runtime.sync import ChatSyncRunner, SyncRunner
from ark.core.utils.context import (
    set_account_id,
    set_resource_id,
    set_resource_type,
)
from ark.telemetry.trace import TraceConfig, setup_tracing


def setup_environment(
    trace_on: bool = True, trace_config: Optional[TraceConfig] = None
) -> None:
    set_resource_type(os.getenv("RESOURCE_TYPE") or "")
    set_resource_id(os.getenv("RESOURCE_ID") or "")
    set_account_id(os.getenv("ACCOUNT_ID") or "")

    setup_tracing(
        endpoint=os.getenv("TRACE_ENDPOINT"),
        trace_on=trace_on,
        trace_config=trace_config,
    )


def initialize(
    context: Any,
    clients: Optional[Dict[str, Tuple[Type[Client], Any]]] = None,
    trace_on: bool = True,
    trace_config: Optional[TraceConfig] = None,
) -> None:
    get_client_pool(
        clients
        or {
            # v3
            "ark": (
                AsyncArk,
                {
                    "base_url": BASE_URL,
                    "max_retries": 3,
                },
            ),
            # v2
            "chat": (
                ArkClient,
                {
                    "host": "maas-api.ml-platform-cn-beijing.volces.com",
                    "auto_refresh_apikey": True,
                },
            ),
            # action
            "action": (
                ArkActionClient,
                {
                    "base_url": BASE_URL,
                    "max_retries": 3,
                },
            ),
        }
    )

    setup_environment(trace_on, trace_config)


def handler(request: RequestType, runner: SyncRunner, context: Context) -> Any:
    try:
        from flask import Response
    except ImportError:
        raise

    try:
        if request.stream:
            return Response(
                runner.generate(request),
                200,
                {
                    "Content-Type": "text/event-stream; charset=utf-8",
                    "X-Tt-Logid": context.request_id,
                },
            )
        else:
            body: Any = runner.run(request)
            return {
                "body": json.dumps(
                    body,
                    ensure_ascii=False,
                    allow_nan=False,
                    indent=None,
                    separators=(",", ":"),
                ),
                "statusCode": 200,
                "headers": {
                    "X-Tt-Logid": context.request_id,
                    "Content-Type": "application/json",
                },
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")


# https://www.volcengine.com/docs/6662/107430
def faas_handler(
    event: Dict[str, Any],
    context: Any,
    runnable_func: Callable[[RequestType], Iterable[ResponseType]],
    clients: Optional[Dict[str, Tuple[Type[Client], Any]]] = None,
    request_cls: Optional[Type[RequestType]] = None,
    runner_cls: Optional[Type[SyncRunner]] = None,
) -> Any:
    initialize(context, clients)

    runner = (
        runner_cls(runnable_func=runnable_func)  # type: ignore
        if runner_cls
        else ChatSyncRunner(runnable_func=runnable_func)  # type: ignore
    )
    request: Request = parse_request(event, request_cls or MaasChatRequest)

    return handler(request, runner, context)
