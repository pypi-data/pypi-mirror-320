import inspect
from inspect import Signature
from typing import AsyncIterable, Callable, Dict, Type

from ark.core.idl.ark_protocol import (
    ArkChatRequest,
)
from ark.core.idl.common_protocol import Request, RequestType, ResponseType
from ark.core.idl.maas_protocol import MaasChatRequest, MaasChatResponse
from ark.core.runtime.asyncio import (
    AsyncRunner,
    ChatAsyncRunner,
    ChatV3AsyncRunner,
    CustomAsyncRunner,
)
from ark.core.task.task import task


@task()
def get_runner(
    runnable_func: Callable[[RequestType], AsyncIterable[ResponseType]],
) -> AsyncRunner:
    signature = inspect.signature(runnable_func)
    request_cls: Type[RequestType] = get_request_cls(signature)
    response_cls: Type[ResponseType] = get_response_cls(signature)

    if issubclass(request_cls, MaasChatRequest) and issubclass(
        response_cls, MaasChatResponse
    ):
        return ChatAsyncRunner(runnable_func)  # type: ignore
    elif issubclass(request_cls, ArkChatRequest):
        return ChatV3AsyncRunner(runnable_func)  # type: ignore
    else:
        return CustomAsyncRunner(response_cls, runnable_func)


@task()
def get_endpoint_config(
    endpoint_path: str,
    runnable_func: Callable[[RequestType], AsyncIterable[ResponseType]],
) -> Dict[str, Type[RequestType]]:
    signature = inspect.signature(runnable_func)
    return {endpoint_path: get_request_cls(signature)}


@task()
def get_request_cls(signature: Signature) -> Type[RequestType]:
    parameters = signature.parameters.values()

    for param in parameters:
        annotation = param.annotation
        assert issubclass(annotation, Request), TypeError(
            "function request should be subclass of request"
        )
        return annotation

    raise Exception("should not reach here")


@task()
def get_response_cls(signature: Signature) -> Type[ResponseType]:
    return_cls = signature.return_annotation
    assert hasattr(return_cls, "__origin__") and issubclass(
        return_cls.__origin__, AsyncIterable
    ), TypeError("function response should be AsyncIterable")
    assert return_cls.__args__ and len(return_cls.__args__) == 1, TypeError(
        "function should return one value"
    )

    # skip response class check
    response_cls = return_cls.__args__[0]
    return response_cls
