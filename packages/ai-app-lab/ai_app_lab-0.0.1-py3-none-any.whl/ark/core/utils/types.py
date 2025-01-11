import json
import logging
import re
from enum import Enum
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterable,
    Generator,
    Iterable,
    List,
    Optional,
    Type,
    Union,
)

import fastapi
from pydantic import BaseModel, ValidationError
from volcenginesdkarkruntime.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
)

from ark.core.idl.ark_protocol import (
    ArkMessage,
    ChatCompletionMessageToolCallParam,
    Function,
)
from ark.core.idl.common_protocol import ChatMessage, RequestType
from ark.core.idl.maas_protocol import MaasChatMessage
from ark.core.utils.errorsv3 import InvalidParameter, MissingParameter

_MAX_DEPTH = 10


def parse_pydantic_error(
    e: ValidationError,
) -> Union[MissingParameter, InvalidParameter]:
    try:
        err = e.errors()[-1]
        err_type, err_loc = err.get("type", ""), err.get("loc", ("",))
        if err_type == "missing":
            return MissingParameter(str(err_loc[-1]))
        else:
            return InvalidParameter(str(err_loc[-1]))
    except Exception as e:
        logging.error(f"parse pydantic error:{e}")
        return InvalidParameter("request")


def dump_json_str(obj: Any) -> str:
    return json.dumps(dump_json(obj), ensure_ascii=False, default=lambda x: str(x))


def dump_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: dump_json(v) for k, v in obj.items()}
    elif isinstance(obj, (tuple, list)):
        return [dump_json(v) for v in obj]
    elif isinstance(obj, BaseModel):
        return obj.model_dump(exclude_unset=True, exclude_none=True)
    elif isinstance(obj, (AsyncGenerator, Generator, AsyncIterable)):
        return str(obj)
    else:
        return obj


# Only for trace
# Truncate all strings to prevent excessively long input/output (e.g., base64 images)
def dump_json_str_truncate(obj: Any, string_length_limit: int) -> str:
    return json.dumps(
        dump_json_truncate(obj, string_length_limit),
        ensure_ascii=False,
        default=lambda x: str(x),
    )


def dump_json_truncate(obj: Any, string_length_limit: int, depth: int = 0) -> Any:
    if depth > _MAX_DEPTH:  # for safety
        return "max recursion depth exceeded"
    if isinstance(obj, dict):
        result_dict = {}
        for k, v in obj.items():
            value = dump_json_truncate(v, string_length_limit, depth + 1)
            if value is not None:
                result_dict[k] = value
        return result_dict
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, (AsyncGenerator, Generator, AsyncIterable)):
        return str(obj)
    elif isinstance(obj, (list, tuple)):
        return [
            dump_json_truncate(item, string_length_limit, depth + 1) for item in obj
        ]
    elif isinstance(obj, str):
        return obj[:string_length_limit]
    elif isinstance(obj, BaseModel) and hasattr(obj, "__dict__"):
        result_dict = {}
        for k, v in obj.__dict__.items():
            value = dump_json_truncate(v, string_length_limit, depth + 1)
            if value is not None:
                result_dict[k] = value
        return result_dict
    else:
        return obj


async def load_request(
    http_request: fastapi.Request,
    req_cls: Type[RequestType],
) -> RequestType:
    if "content-type" not in http_request.headers:
        raise InvalidParameter("Invalid request: missing content-type")
    content_type, body = (
        http_request.headers.get("content-type", ""),
        await http_request.body(),
    )
    media_type = content_type.split(";")[0].strip()
    try:
        if media_type == "application/json":
            return req_cls.model_validate_json(body)
    except ValidationError as e:
        raise parse_pydantic_error(e)
    raise InvalidParameter(f"Invalid request: invalid content-type={content_type}")


def transform_response(response: Any) -> str:
    if isinstance(response, str):
        return response
    elif isinstance(response, dict):
        return json.dumps(response)
    elif isinstance(response, BaseModel):
        return response.model_dump_json(exclude_none=True, exclude_unset=True)
    else:
        return dump_json_str(response)


def convert_messages(
    messages: Optional[List[MaasChatMessage]] = None,
) -> List[ChatMessage]:
    if messages is None:
        raise ValueError("messages are required")

    result: List[ChatMessage] = []
    for message in messages:
        if not isinstance(message.content, str):
            continue
        result.append(ChatMessage(role=message.role, content=message.content))

    return result


def convert_response_message(
    response_message: Union[ChatCompletionChunk, ChatCompletion],
) -> ArkMessage:
    return ArkMessage(
        role=response_message.role,
        content=response_message.content,
        tool_calls=[
            ChatCompletionMessageToolCallParam(
                id=tool_call.id,
                type=tool_call.type,
                function=Function(**tool_call.function.__dict__),
            )
            for tool_call in response_message.tool_calls
        ]
        if response_message.tool_calls
        else None,
    )


def snake_merge(merge_lists: Iterable[List[Any]]) -> List[Any]:
    result = []
    max_length = max(
        len(merge_list) if merge_list is not None else 0 for merge_list in merge_lists
    )
    for i in range(max_length):
        for merge_list in merge_lists:
            if merge_list is None:
                continue
            if i < len(merge_list):
                result.append(merge_list[i])
    return result


def camel_to_snake_case(obj: Any, ignore_value: bool = False) -> Any:
    # Use regularized expression to convert camelCase to snake_case
    # Add '_' before Upper case letters and change all letters to lowercase

    if isinstance(obj, BaseModel):
        return camel_to_snake_case(obj.dict(exclude_unset=True))
    elif isinstance(obj, dict):
        return {
            camel_to_snake_case(k): v
            if ignore_value and isinstance(v, str)
            else camel_to_snake_case(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, (tuple, list)):
        return [camel_to_snake_case(v) for v in obj]
    elif isinstance(obj, str):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", obj).lower()
    else:
        return obj
