"protocol for GPTEngine"

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator
from typing_extensions import Literal

from ark.core.idl.common_protocol import (
    ActionUsage,
    BotUsage,
    ChatMessageContent,
    ChatRole,
    ChatUsage,
    Embedding,
    Error,
    FunctionCall,
    LabelLogprobosValue,
    Parameters,
    Reference,
    Request,
    Response,
    Tool,
)


# maas handler protocol
class ToolCall(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    function: Optional[FunctionCall] = None


class MaasChatMessage(BaseModel):
    role: Optional[ChatRole] = None
    content: Optional[Union[str, List[ChatMessageContent]]] = None
    name: Optional[str] = None
    references: Optional[List[Reference]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class MaasChatRequest(Request):
    messages: List[MaasChatMessage]
    stream: bool = False
    verbose: bool = False
    crypto_token: Optional[str] = None
    tools: Optional[List[Tool]] = None
    parameters: Optional[Union[Parameters, Dict[str, Any]]] = None
    user: Optional[str] = None
    extra: Dict[str, str] = Field(default_factory=dict)

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @field_validator("messages")
    def validate_messages(
        cls, v: Optional[List[MaasChatMessage]]
    ) -> Optional[List[MaasChatMessage]]:
        if not v:
            raise ValueError("Messages are required")

        pre_role = None  # user, assistant, function, system
        for msg in v:
            if not msg.role:
                raise ValueError("Role is required")
            if msg.content is None:
                msg.content = ""

            if msg.role == ChatRole.SYSTEM:
                continue

            if msg.role == ChatRole.FUNCTION:
                assert (
                    pre_role == ChatRole.ASSISTANT
                ), "Function message should follow an assistant message"

            pre_role = msg.role

        return v

    def get_user_info_extra(self) -> Optional[UserInfoExtra]:
        if not self.extra or not self.extra.get("user_info"):
            return None
        return UserInfoExtra.model_validate_json(self.extra.get("user_info", ""))

    def is_emit_intention_signal_extra(self) -> bool:
        return self.extra.get("emit_intention_signal_extra", "false") == "true"


class Logprobs(BaseModel):
    text_offset: Optional[List[int]] = None
    token_logprobs: Optional[List[float]] = None
    tokens: Optional[List[str]] = None
    top_logprobs: Optional[List[Dict[str, Any]]] = None


class MaasChatChoiceLog(BaseModel):
    stage: Optional[str] = None
    input: Optional[str] = None
    content: Optional[str] = None


class MaasChatChoice(BaseModel):
    index: Optional[int] = None
    message: MaasChatMessage
    finish_reason: Optional[str] = None
    logprobs: Optional[Logprobs] = None
    action: Optional[MaasChatChoiceLog] = None
    observation: Optional[MaasChatChoiceLog] = None
    thought: Optional[MaasChatChoiceLog] = None


class MaasChatResponse(Response):
    req_id: Optional[str] = None
    error: Optional[Error] = None
    choices: List[MaasChatChoice] = Field(default_factory=list)
    usage: Optional[Union[ChatUsage, BotUsage]] = None
    extra: Optional[Dict[str, str]] = None

    @staticmethod
    def merge(responses: List[MaasChatResponse]) -> MaasChatResponse:
        merged = responses[0]
        for resp in responses[1:]:
            for i, j in zip(merged.choices, resp.choices):
                if isinstance(i.message.content, str) and isinstance(
                    j.message.content, str
                ):
                    i.message.content += j.message.content
                elif isinstance(i.message.content, list) and isinstance(
                    j.message.content, list
                ):
                    i.message.content.extend(j.message.content)
                else:
                    raise TypeError("no supported merge type")
                i.finish_reason = j.finish_reason
        merged.usage = responses[-1].usage
        merged.extra = responses[-1].extra
        return merged

    def transform_bot_usage(self) -> None:
        if not self.usage:
            return
        if isinstance(self.usage, BotUsage):
            return
        self.usage = BotUsage(model_usage=[self.usage])
        return

    def set_extra(self, key: str, value: str) -> None:
        if not self.extra:
            self.extra = dict()
        self.extra[key] = value


class MaasCertRequest(Request):
    pass


class MaasCertResponse(Response):
    cert: str = ""


class MaasClassificationRequest(Request):
    query: Optional[str] = None
    labels: List[str]


class MaasClassificationResponse(Response):
    req_id: Optional[str] = None
    label: Optional[str] = None
    label_logprobos: Optional[Dict[str, LabelLogprobosValue]] = None
    usage: Optional[ChatUsage] = None
    error: Optional[Error] = None


class MaasTokenizeRequest(Request):
    text: Optional[str] = None


class MaasTokenizeResponse(Response):
    req_id: Optional[str] = None
    total_tokens: Optional[int] = None
    tokens: Optional[List[str]] = None
    token_ids: Optional[List[int]] = None
    offset_mapping: Optional[List[List[int]]] = None
    error: Optional[Error] = None


class MaasEmbeddingsRequest(Request):
    input: Optional[List[str]] = None
    encoding_format: Optional[str] = None
    user: Optional[str] = None


class MaasEmbeddingsResponse(Response):
    req_id: Optional[str] = None
    usage: Optional[ChatUsage] = None
    error: Optional[Error] = None
    object: Optional[str] = None
    data: Optional[List[Embedding]] = None


class UserInfoExtra(BaseModel):
    city: str = ""
    district: str = ""


SourceType = Literal[
    "weather",
    "douyin_baike",
    "toutiao_article",
    "douyin_short_video",
    "search_engine",
    "xigua_feed_video",
    "toutiao_short_content",
]

SOURCE_TAG = {
    "search_engine": "搜索引擎",
    "weather": "墨迹天气",
    "toutiao_article": "头条图文",
    "douyin_short_video": "抖音视频",
    "douyin_baike": "抖音百科",
    "xigua_feed_video": "西瓜视频",
    "toutiao_short_content": "微头条",
}

SearchAction = Literal["WebBrowsingPlus", "WebBrowsingPro", "content_plugin"]


class SearchRequest(Request):
    question: str = ""
    action_name: SearchAction = Field(default="WebBrowsingPlus")
    source_type: Optional[List[SourceType]] = None
    summary_top_k: int = 10
    utm_source: Optional[str] = None
    keywords: Optional[List[str]] = None
    user_info: Optional[UserInfoExtra] = None


class SearchResponse(Response):
    search_results: List[str] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    search_usage: Optional[List[ActionUsage]] = None


class KnowledgeBaseResponse(Response):
    texts: List[str] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
