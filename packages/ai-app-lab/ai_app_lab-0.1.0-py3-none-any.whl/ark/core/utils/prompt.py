import json
import logging
import warnings
from typing import Any, Dict, List, Set, Union

from langchain.prompts.chat import BaseChatPromptTemplate
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.messages.tool import ToolCall
from typing_extensions import Literal

from ark.core.idl.ark_protocol import ArkMessage, ChatCompletionMessageToolCallParam
from ark.core.idl.common_protocol import ChatRole
from ark.core.idl.maas_protocol import MaasChatMessage
from ark.core.task import task
from ark.core.utils.errorsv3 import InvalidParameter

MessageRole2ChatRole = {
    "human": ChatRole.USER,
    "ai": ChatRole.ASSISTANT,
    "system": ChatRole.SYSTEM,
    "function": ChatRole.FUNCTION,
}


def _convert_message_role_to_ark_role(  # type: ignore
    message_role: str,
) -> Literal["user", "system", "assistant", "tool"]:  # type: ignore
    if message_role == "human":
        return "user"
    elif message_role == "ai":
        return "assistant"
    elif message_role == "system":
        return "system"
    elif message_role == "tool" or message_role == "function":
        return "tool"


def maas_chat_messages_to_messages(
    chat_messages: Union[List[MaasChatMessage], List[ArkMessage]],
) -> List[BaseMessage]:
    """Convert llmflow engine chat request to langchain list of messages"""
    messages: List[BaseMessage] = []

    # Check if messages is None
    if chat_messages is None:
        raise ValueError("messages")

    for msg in chat_messages:
        if msg.content is None:
            warnings.warn(
                "ChatMessage contains content as None, replace it with empty str"
            )
            msg.content = ""

        kwargs = {"choice": {"message": msg.dict()}}
        if not isinstance(msg.content, str):
            continue
        if msg.role == ChatRole.ASSISTANT:
            messages.append(AIMessage(content=msg.content, additional_kwargs=kwargs))
        elif msg.role == ChatRole.SYSTEM:
            messages.append(
                SystemMessage(content=msg.content, additional_kwargs=kwargs)
            )
        elif msg.role == ChatRole.USER:
            messages.append(HumanMessage(content=msg.content, additional_kwargs=kwargs))
        elif msg.role == ChatRole.FUNCTION or msg.role == ChatRole.TOOL:
            messages.append(
                FunctionMessage(
                    name=msg.name if "name" in msg.model_fields and msg.name else "",
                    content=msg.content,
                    additional_kwargs=kwargs,
                )
            )
        else:
            raise ValueError(f"role: {msg.role}")
    return messages


def _convert_ark_messages(chat_messages: List[ArkMessage]) -> List[BaseMessage]:
    messages: List[BaseMessage] = []
    tool_calls: Dict[str, ChatCompletionMessageToolCallParam] = {}
    next_tool_ids: Set[str] = set()
    for message in chat_messages:
        if len(next_tool_ids) > 0 and message.role != "tool":
            raise InvalidParameter(
                parameter="messages",
                cause="An assistant message with 'tool_calls' must "
                "be followed by tool messages responding to each 'tool_call_id'.",
            )

        if message.role == "user":
            if isinstance(message.content, str):
                messages.append(
                    HumanMessage(content=message.content, name=message.name)
                )
            else:
                messages.append(
                    HumanMessage(
                        content=[
                            part.model_dump(exclude_none=True, exclude_unset=True)
                            for part in message.content
                        ]
                    )
                )

        elif message.role == "assistant":
            next_tool_ids = set()

            def load_arguments(arguments: str) -> Dict[str, Any]:
                try:
                    args = json.loads(arguments)
                    if isinstance(args, dict) and all(
                        isinstance(key, str) for key in args.keys()
                    ):
                        return args
                    return {}
                except json.JSONDecodeError:
                    logging.error(
                        f"json decode arguments failed: arguments={arguments}"
                    )
                    return {}

            content, thought = (message.content or ""), ""
            if message.tool_calls is not None:
                if isinstance(message.content, str):
                    sep = message.content.rfind("\n")
                    if sep >= 0:
                        content, thought = (
                            message.content[:sep],
                            message.content[sep + 1 :],
                        )

                for tool_call in message.tool_calls:
                    tool_calls[tool_call.id] = tool_call
                    next_tool_ids.add(tool_call.id)

            messages.append(
                AIMessage(
                    content=content,  # type: ignore
                    name=message.name,
                    tool_calls=[
                        ToolCall(
                            name=tool_call.function.name,
                            args=(
                                load_arguments(tool_call.function.arguments)
                                if tool_call.function.arguments
                                else {}
                            ),
                            id=tool_call.id,
                        )
                        for tool_call in (message.tool_calls or [])
                    ],
                    additional_kwargs={
                        "choice": {
                            "message": {
                                "tool_calls": [
                                    {
                                        "id": tool_call.id,
                                        "type": tool_call.type,
                                        "function": {
                                            "name": tool_call.function.name,
                                            "arguments": tool_call.function.arguments,
                                            "thought": thought,
                                        },
                                    }
                                    for tool_call in (message.tool_calls or [])
                                ],
                            }
                        }
                    },
                )
            )
        elif message.role == "system":
            messages.append(
                SystemMessage(
                    content=message.content,  # type: ignore
                )
            )
        elif message.role == "tool":
            if message.tool_call_id not in tool_calls:
                raise InvalidParameter(
                    parameter="tool_call_id",
                    cause=f"Invalid parameter: 'tool_call_id' of {message.tool_call_id}"
                    f" not found in 'tool_calls' of previous message",
                )
            next_tool_ids.remove(message.tool_call_id)

            tool_call = tool_calls[message.tool_call_id]

            assert tool_call.type == "function", TypeError(
                f"expect `function`, got {tool_call.type}"
            )

            messages.append(
                FunctionMessage(
                    content=message.content,  # type: ignore
                    name=tool_call.function.name,
                )
            )

    if len(next_tool_ids) > 0:
        raise InvalidParameter(
            parameter="messages",
            cause="An assistant message with 'tool_calls' must be followed"
            " by tool messages responding to each 'tool_call_id'.",
        )

    return messages


@task()
def format_maas_prompts(
    template: BaseChatPromptTemplate,
    chat_messages: List[MaasChatMessage],
    **kwargs: Any,
) -> List[MaasChatMessage]:
    messages = template.format_messages(
        messages=maas_chat_messages_to_messages(chat_messages), **kwargs
    )

    prompts = [
        MaasChatMessage(
            role=MessageRole2ChatRole.get(message.type),
            content=message.content if isinstance(message.content, str) else "",
            name=message.name,
        )
        for message in messages
    ]

    return prompts


@task()
def format_ark_prompts(
    template: BaseChatPromptTemplate,
    chat_messages: List[ArkMessage],
    **kwargs: Any,
) -> List[ArkMessage]:
    messages = template.format_messages(
        messages=_convert_ark_messages(chat_messages), **kwargs
    )

    prompts = [
        ArkMessage(
            role=_convert_message_role_to_ark_role(message.type),
            content=message.content if isinstance(message.content, str) else "",
        )
        for message in messages
    ]

    return prompts
