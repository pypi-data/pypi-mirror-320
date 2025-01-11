from typing import Dict, Optional, Union

from volcenginesdkarkruntime.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
)

from ark.component.v3.llm.base import BaseChatLanguageModel, handle_function_call
from ark.core.idl.ark_protocol import (
    ArkChatCompletionChunk,
    ArkChatRequest,
    ArkChatResponse,
    CallableFunction,
    FunctionCallMode,
)
from ark.core.idl.common_protocol import ActionUsage


class ActionCall(BaseChatLanguageModel):
    async def handle_function_call(
        self,
        request: ArkChatRequest,
        response: Union[
            ChatCompletionChunk, ChatCompletion, ArkChatCompletionChunk, ArkChatResponse
        ],
        available_functions: Optional[Dict[str, CallableFunction]] = None,
        function_call_mode: Optional[FunctionCallMode] = FunctionCallMode.SEQUENTIAL,
    ) -> bool:
        is_more_request = await handle_function_call(
            request,
            response,
            available_functions,
            function_call_mode,
            include_details=True,
        )
        if (
            isinstance(response, ArkChatCompletionChunk)
            and response.bot_usage
            and response.bot_usage.action_details
        ):
            response.bot_usage.action_usage = [
                ActionUsage(count=1, name=detail.name)
                for detail in response.bot_usage.action_details
            ]
        return is_more_request
