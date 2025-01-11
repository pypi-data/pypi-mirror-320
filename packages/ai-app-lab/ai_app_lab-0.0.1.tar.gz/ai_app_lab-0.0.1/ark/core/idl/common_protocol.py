"common protocol for GPTEngine"

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field, field_validator
from volcenginesdkarkruntime.types.completion_usage import CompletionUsage


class Embedding(BaseModel):
    index: Optional[int] = None
    embedding: List[float] = Field(default_factory=list)
    object: Optional[str] = None


class UserInfo(BaseModel):
    accountId: str
    userId: str
    authorization_token: str = Field(repr=False, exclude=True)


class FunctionCall(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None


class Server(BaseModel):
    url: str
    description: Optional[str] = None


class Action(BaseModel):
    server: Server
    http_method: str = Field(default="POST")
    path: str
    tool: Tool


class Function(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict] = None
    examples: Optional[List[str]] = None


class Tool(BaseModel):
    type: str
    function: Optional[Function] = None
    options: Optional[Dict[str, Any]] = None


class ApiCall(BaseModel):
    name: str
    headers: Optional[Any] = None
    parameters: Optional[Any] = None
    json_datas: Optional[Any] = None


class CoverImage(BaseModel):
    url: str = ""
    width: int = 0
    height: int = 0


class Reference(BaseModel):
    url: Optional[str] = None
    idx: Optional[int] = None
    logo_url: Optional[str] = None
    mobile_url: Optional[str] = None
    site_name: Optional[str] = Field(default=None, description="来源")
    title: Optional[str] = Field(default=None, description="标题")
    summary: Optional[str] = None
    publish_time: Optional[str] = Field(default=None, description="发布时间")
    cover_image: Optional[CoverImage] = None
    freshness_info: Optional[str] = Field(default=None, description="时效性")
    extra: Optional[Dict[str, Any]] = None

    # deprecated
    pc_url: Optional[str] = None

    # knowledge base
    doc_id: Optional[str] = Field(default=None, description="文档ID")
    doc_name: Optional[str] = Field(default=None, description="文档名")
    doc_type: Optional[str] = Field(default=None, description="文档类型")
    doc_title: Optional[str] = Field(default=None, description="文档标题")
    chunk_title: Optional[str] = Field(default=None, description="分块标题")
    chunk_id: Optional[str] = Field(default=None, description="分块编号")
    collection_name: Optional[str] = None
    project: Optional[str] = None


class File(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    uri: Optional[str] = None


class Error(BaseModel):
    code: str
    code_n: Optional[int] = None
    message: str


class ArkError(BaseModel):
    code: str
    message: str
    param: Optional[str] = None
    type: Optional[str] = None


class Request(BaseModel):
    stream: bool = False


class Response(BaseModel):
    error: Optional[Union[Error, ArkError]] = None


class ModelDesc(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    endpoint_id: Optional[str] = None
    authorization_token: Optional[str] = None


class ChatMessageImageContent(BaseModel):
    url: Optional[str] = None
    detail: Optional[str] = None
    image_bytes: Optional[bytes] = None


class ChatMessageContent(BaseModel):
    type: Optional[str] = None
    text: Optional[str] = None
    image_url: Optional[ChatMessageImageContent] = None


class Parameters(BaseModel):
    max_prompt_tokens: Optional[int] = None
    max_new_tokens: Optional[int] = None
    min_new_tokens: Optional[int] = None
    max_tokens: Optional[int] = None

    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None

    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    repetition_penalty: Optional[float] = None
    do_sample: Optional[bool] = None
    logprobs: Optional[int] = None

    stop: Optional[List[str]] = None
    logit_bias: Optional[Dict[int, float]] = None
    guidance: Optional[bool] = None

    def merge_from(self, other: Union[Dict, Parameters]) -> Parameters:
        other_dict = other if isinstance(other, Dict) else other.dict()
        merged_dict = self.dict()

        for key in merged_dict.keys():
            value = other_dict.get(key, None)
            if value is not None:
                merged_dict[key] = value

        return self.__class__(**merged_dict)

    def merge_to(self, other: Union[Dict, Parameters]) -> Parameters:
        self_dict = self.dict()
        merged_dict = other if isinstance(other, Dict) else other.dict()

        for key in self_dict.keys():
            value = self_dict.get(key, None)
            if value is not None:
                merged_dict[key] = value

        return self.__class__(**merged_dict)


class ChatRole(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
    FUNCTION = "function"
    TOOL = "tool"


class ChatUsage(BaseModel):
    name: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __iadd__(self, others: Union[ChatUsage, List[ChatUsage]]) -> ChatUsage:
        if not isinstance(others, list):
            others = [others]

        for usage in others:
            self.prompt_tokens += usage.prompt_tokens
            self.completion_tokens += usage.completion_tokens
            self.total_tokens += usage.total_tokens

        return self

    def __add__(self, others: Union[ChatUsage, List[ChatUsage]]) -> ChatUsage:
        if not isinstance(others, list):
            others = [others]

        total_usage = ChatUsage(
            name=self.name,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.total_tokens,
        )
        for usage in others:
            total_usage.prompt_tokens += usage.prompt_tokens
            total_usage.completion_tokens += usage.completion_tokens
            total_usage.total_tokens += usage.total_tokens

        return total_usage


class ToolOutputType(str, Enum):
    TOOL = "tool"
    EXCEPTION = "exception"


class ToolOutput(BaseModel):
    type: ToolOutputType
    data: Optional[Union[Any, ExceptionInfo]] = None


class ExceptionInfo(BaseModel):
    type: Optional[str] = None
    message: Optional[str] = None


class ActionUsage(BaseModel):
    # deprecated
    name: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    search_count: Optional[int] = None

    # latest
    action_name: Optional[str] = None
    """
    action name 
    """
    count: Optional[int] = None
    """
    count for calling the action
    """

    def __iadd__(
        self, others: Union[ActionUsage, List[ActionUsage]]
    ) -> List[ActionUsage]:
        if not isinstance(others, list):
            return [self, others]
        else:
            others.append(self)
            return others

    def __add__(
        self, others: Union[ActionUsage, List[ActionUsage]]
    ) -> List[ActionUsage]:
        if not isinstance(others, list):
            return [self, others]
        else:
            others.append(self)
            return others


class ActionDetails(BaseModel):
    name: str
    """
    action name, e.g. "WebBrowsingPlus"
    """
    count: int = 0
    """
    count for calling the action, e.g. 1
    """
    tool_details: List[ToolDetails] = Field(default_factory=list)
    """
    details about calling the tool
    """


class ToolDetails(BaseModel):
    name: str
    """
    tool name, e.g. "Search"
    """
    input: Any
    """
    input for calling the tool
    """
    output: Union[Any, ToolOutput]
    """
    output for calling the tool
    """
    created_at: Optional[int] = None
    """
    created time in milliseconds since the Epoch.
    """
    completed_at: Optional[int] = None
    """
    completed time in milliseconds since the Epoch.
    """


class BotUsage(BaseModel):
    model_usage: Optional[List[Union[ChatUsage, CompletionUsage]]] = Field(
        default_factory=list
    )
    action_usage: Optional[List[ActionUsage]] = Field(default_factory=list)
    action_details: Optional[List[ActionDetails]] = Field(default_factory=list)

    def __iadd__(self, others: Union[BotUsage, List[BotUsage]]) -> BotUsage:
        if not isinstance(others, list):
            others = [others]

        for usage in others:
            if self.model_usage and usage.model_usage:
                self.model_usage.extend(usage.model_usage)
            elif usage.model_usage:
                self.model_usage = usage.model_usage

            if self.action_usage and usage.action_usage:
                self.action_usage.extend(usage.action_usage)
            elif usage.action_usage:
                self.action_usage = usage.action_usage

            if self.action_details and usage.action_details:
                self.action_details.extend(usage.action_details)
            elif usage.action_details:
                self.action_details = usage.action_details

        return self

    def __add__(self, others: Union[BotUsage, List[BotUsage]]) -> BotUsage:
        if not isinstance(others, list):
            others = [others]

        total_usage = BotUsage(
            model_usage=self.model_usage or [],
            action_usage=self.action_usage or [],
            action_details=self.action_details or [],
        )
        for usage in others:
            if (
                usage.action_usage
                and total_usage.action_usage
                and len(usage.action_usage) > 0
            ):
                total_usage.action_usage.extend(usage.action_usage)
            if (
                usage.model_usage
                and total_usage.model_usage
                and len(usage.model_usage) > 0
            ):
                total_usage.model_usage.extend(usage.model_usage)
            if (
                usage.action_details
                and total_usage.action_details
                and len(usage.action_details) > 0
            ):
                total_usage.action_details.extend(usage.action_details)

        return total_usage


class Logprobs(BaseModel):
    text_offset: Optional[List[int]] = None
    token_logprobs: Optional[List[float]] = None
    tokens: Optional[List[str]] = None
    top_logprobs: Optional[List[Dict[str, Any]]] = None


class CertRequest(Request):
    model: Union[ModelDesc, None] = None


class CertResponse(Response):
    model: Union[ModelDesc, None] = None
    cert: str = ""


class ClassificationRequest(Request):
    model: Union[ModelDesc, None] = None
    req_id: Optional[str] = None
    query: Optional[str] = None
    labels: List[str] = Field(default_factory=list)


class ClassificationResponse(Response):
    label: Optional[str] = None
    label_logprobos: Optional[Dict[str, LabelLogprobosValue]] = None
    usage: Optional[ChatUsage] = None
    req_id: Optional[str] = None
    error: Optional[Error] = None


class TokenizationRequest(Request):
    model: Union[ModelDesc, None] = None
    req_id: Optional[str] = None
    text: Optional[str] = None


class TokenizationResponse(Response):
    total_tokens: Optional[int] = None
    tokens: Optional[List[str]] = None
    token_ids: Optional[List[int]] = None
    offset_mapping: Optional[List[List[int]]] = None
    req_id: Optional[str] = None
    error: Optional[Error] = None


class EmbeddingsRequest(Request):
    model: Union[ModelDesc, None] = None
    req_id: Optional[str] = None
    input: Optional[List[str]] = None
    encoding_format: Optional[str] = None
    user: Optional[str] = None


class EmbeddingsResponse(Response):
    usage: Optional[ChatUsage] = None
    req_id: Optional[str] = None
    error: Optional[Error] = None
    object: Optional[str] = None
    data: Optional[List[Embedding]] = None


class LabelLogprobosValue(BaseModel):
    tokens: List[str] = Field(default_factory=list)
    token_logprobs: List[float] = Field(default_factory=list)
    req_id: Optional[str] = None


class ChatMessage(BaseModel):
    role: Optional[ChatRole] = None
    content: str = Field(repr=False, default=None)
    multi_contents: Optional[List[ChatMessageContent]] = None
    name: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    references: Optional[List[Reference]] = None
    reference: Optional[Reference] = None
    files: Optional[List[File]] = None


class ChatRequest(Request):
    model: ModelDesc
    messages: Optional[List[ChatMessage]] = None
    parameters: Optional[Parameters] = None
    stream: bool = False
    req_id: Optional[str] = None
    crypto_token: Optional[str] = None
    functions: Optional[List[Function]] = None
    tools: Optional[List[Tool]] = None
    plugins: Optional[List[str]] = None
    model_arch: Optional[str] = None

    extra: Optional[Dict[str, str]] = None

    def set_extra(self, key: str, value: str) -> None:
        if self.extra is None:
            self.extra = {}
        self.extra[key] = value

    @field_validator("model")
    def validate_model(cls, v: Optional[ModelDesc]) -> Optional[ModelDesc]:
        if not v:
            raise ValueError("Model is required")
        if not v.name and not v.endpoint_id:
            raise ValueError("Model name or endpoint_id is required")
        return v

    @field_validator("messages")
    def validate_messages(
        cls, v: Optional[List[ChatMessage]]
    ) -> Optional[List[ChatMessage]]:
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


class ChatChoice(BaseModel):
    index: Optional[int] = None
    message: ChatMessage
    finish_reason: Optional[str] = None
    logprobs: Optional[Logprobs] = None


class ChatResponse(Response):
    req_id: str = ""
    created: Optional[int] = None
    error: Optional[Error] = None
    choice: Optional[ChatChoice] = None
    choices: List[ChatChoice] = Field(default_factory=list)
    usage: Optional[ChatUsage] = None
    extra: Optional[Dict[str, str]] = None

    def set_extra(self, key: str, value: str) -> None:
        if self.extra is None:
            self.extra = dict()
        self.extra[key] = value

    @staticmethod
    def merge(responses: List[ChatResponse]) -> ChatResponse:
        merged = responses[0]
        for resp in responses[1:]:
            for i, j in zip(merged.choices, resp.choices):
                i.message.content += j.message.content
                i.finish_reason = j.finish_reason
        merged.usage = responses[-1].usage
        return merged


class JsonDType(str, Enum):
    Object = "object"
    Number = "number"
    Integer = "integer"
    String = "string"
    Array = "array"
    Null = "null"
    Boolean = "boolean"


class AudioMediaType(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    AAC = "aac"
    OGG_OPUS = "ogg_opus"
    PCM = "pcm"


class JsonDefinition(BaseModel):
    # Type specifies the data type of the schema.
    type: JsonDType
    # Description is the description of the schema.
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    properties: Optional[Dict[str, JsonDefinition]] = None
    required: Optional[List[str]] = None
    items: Optional[JsonDefinition] = None
    property_order: Optional[List[str]] = None


class ToolCall(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    function: Optional[FunctionCall] = None


class Context(BaseModel):
    request_id: str = ""
    client_request_id: str = ""
    account_id: str = ""
    resource_id: str = ""
    resource_type: str = ""


RequestType = TypeVar("RequestType", bound=Request, contravariant=True)
ResponseType = TypeVar("ResponseType", bound=Response, covariant=True)
