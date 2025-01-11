"errors"

from enum import IntEnum
from typing import Optional, Union

from ark.core._api.deprecation import deprecated
from ark.core.idl.common_protocol import Error
from ark.core.utils import context


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.core.utils.errorsv3.ErrorCode",
)
class GptCode(IntEnum):
    http_code: int
    description: Optional[str]

    def __new__(
        cls, code_n: int, http_code: int = 500, description: str = ""
    ) -> "GptCode":
        obj = int.__new__(cls, code_n)
        obj._value_ = code_n

        obj.http_code = http_code
        obj.description = description
        return obj

    SignatureDoesNotMatch = (
        1709801,
        401,
        "Request signature we calculated does not match the signature you provided",
    )
    RequestTimeout = (
        1709802,
        408,
        "Request to service is timeout: it may happen on service is meeting heavy load",
    )
    InferenceServiceConnetionTimeout = (
        1709803,
        504,
        "Connection to service is timeout",
    )
    MissingAuthenticationHeader = (
        1709804,
        401,
        "Request is missing authentication header",
    )
    AuthenticationHeaderIsInvalid = (
        1709805,
        401,
        "Request authentication header content is invalid",
    )
    InternalServiceError = (1709806, 500, "Service has some internal Error")
    MissingParameter = 1709807, 400, "The request is missing parameter"
    InvalidParameter = (
        1709808,
        400,
        "A parameter specified in the request is not valid",
    )
    AuthenticationExpire = (1709809, 401, "You are failed to authentication")
    EndpointIsInvalid = (1709810, 400, "The specific endpoint is not exist or invalid")
    EndpointIsNotEnable = (1709811, 503, "The specific endpoint is closed")
    ChatNotSupportStreamMode = (1709812, 400, "Model not support stream mode")
    ReqTextExistRisk = (
        1709813,
        400,
        "The input text may contain sensitive information",
    )
    RespTextExistRisk = (
        1709814,
        400,
        "The output text may contain sensitive information",
    )
    EndpointRateLimitExceeded = 1709815, 429, "The request is throttled"
    ServiceConnectionRefused = (1709816, 503, "Connection to service is refused")
    ServiceConnectionClosed = (1709817, 502, "Connection to service is closed")
    UnauthorizedUserForEndpoint = (1709818, 401, "Failed to access endpoint")
    InvalidEndpointWithNoURL = (1709819, 401, "Endpoint is invalid")
    EndpointAccountRpmRateLimitExceeded = (
        1709820,
        429,
        "RPM (Requests Per Minute) limit of the account is exceeded",
    )
    EndpointAccountTpmRateLimitExceeded = (
        1709821,
        429,
        "TPM (Tokens Per Minute) limit of the account is exceeded",
    )
    ServiceResourceWaitQueueFull = (
        1709822,
        412,
        "Service has no more resource for more request put into queue",
    )
    EndpointIsPending = (1709823, 503, "The specific endpoint is pending")
    ServiceNotOpen = (1709824, 503, "The free trial quota has been consumed")
    MaasPlatformNotOpen = (
        1709825,
        503,
        "The user has not opened the maas platform service",
    )
    LowPriorityLimitExceeded = (
        1709826,
        429,
        "The request is throttled by low priority limiter",
    )
    TextCheckServiceError = (1709827, 500, "Fail to request business security service")
    APINotSupport = (1709828, 405, "API not supported")
    ModelNotSupportEmbeddings = (1709829, 405, "Model not support embeddings")
    UnauthorizedClientCertificate = (1709901, 401, "You are failed to authentication")
    InternalServiceShowMsgError = (1709902, 500, "Service has some internal")
    ChatNotSupportBatchStreamMode = (
        1709903,
        405,
        "Model not support batch stream mode",
    )
    ChatNotSupportBatchMode = (1709904, 405, "Model not support batch mode")
    RequestCanceled = (1709905, 500, "The request is canceled before response")
    NeedRetryError = (1709906, 500, "The request can retry afterwards")
    NoAccountIdError = (1709907, 500, "No AccountId in context")
    NoUserIdError = (1709908, 500, "No UserId in context")

    Unknown = (1709600, 500, "Unknown error")
    EngineInternalServiceError = (1709601, 500, "Engine internal service error")
    FunctionCallPostProcessError = (1709602, 500, "Function call post process error")
    ModelLoadingError = (
        1709912,
        503,
        "loading model, please try again later, or contact with administrator",
    )

    ImageSizeLimitExceeded = (
        1709830,
        400,
        (
            "The Image size exceeds limit, please reduce the image size, "
            "or contact with administrator"
        ),
    )
    ImageFormatNotSupported = (
        1709831,
        400,
        (
            "The Image format not supported, only (jpg, png), please modify image, "
            "or contact with administrator"
        ),
    )
    OnlyOneImageSupported = (
        1709832,
        400,
        (
            "Only one image supported in a session, please modify image, "
            "or contact with administrator"
        ),
    )
    OnlyOneMultiContentSupported = (
        1709833,
        400,
        (
            "Only one content supported in a session, please modify, "
            "or contact with administrator"
        ),
    )
    UrlUnSupported = (
        1709834,
        400,
        (
            "Only tos, http, https url supported, please modify, "
            "or contact with administrator"
        ),
    )
    OperationDenied = (
        1709835,
        403,
        ("Operation is denied."),
    )
    KnowledgeBaseError = (
        1709836,
        500,
        "Calling KnowledgeBase meet error",
    )
    ResourceNotFound = (
        1709837,
        404,
        "The specified resource is not found.",
    )
    AssistantRateLimitExceeded = (
        1709838,
        429,
        "Request limit of assistant is exceeded",
    )
    ActionRateLimitExceeded = (
        1709839,
        429,
        "Request limit of action is exceeded",
    )
    UnauthorizedUserForResource = (
        1709840,
        401,
        "Failed to access resource: not pass the authorization check.",
    )


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.core.utils.errorsv3.APIException",
)
class GPTException(Exception):
    def __init__(self, message: str, code_n: Union[GptCode, int]):
        super().__init__(message)
        self.message = message
        self.resource_id = context.get_resource_id()
        self.account_id = context.get_account_id() or ""

        if isinstance(code_n, GptCode):
            code_n = code_n
        else:
            try:
                code_n = GptCode(code_n)
            except ValueError:
                code_n = GptCode.Unknown

        self.code_n = code_n

    @property
    def code(self) -> str:
        return self.code_n.name

    @property
    def http_code(self) -> int:
        return self.code_n.http_code

    def __str__(self) -> str:
        return (
            "Detailed exception information is listed below.\n"
            + "account_id: {}\n"
            + "resource_id: {}\n"
            + "code_n: {}\n"
            + "code: {}\n"
            + "message: {}"
        ).format(
            self.account_id, self.resource_id, self.code_n, self.code, self.message
        )

    def to_error(self) -> Error:
        return Error(
            code=self.code,
            code_n=self.code_n.value,
            message=self.message,
        )


class InternalServiceError(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.EngineInternalServiceError)


class InvalidParameter(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.InvalidParameter)


class MissingParameter(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.MissingParameter)


class OperationDenied(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.OperationDenied)


class KnowledgeBaseError(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.KnowledgeBaseError)


class RequestTimeout(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.RequestTimeout)


class FunctionCallPostProcessError(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.FunctionCallPostProcessError)


class ReqTextExistRisk(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.ReqTextExistRisk)


class RespTextExistRisk(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.RespTextExistRisk)


class TextCheckServiceError(GPTException):
    def __init__(self, message: str):
        super().__init__(message, code_n=GptCode.TextCheckServiceError)


class RagException(Exception):
    def __init__(self, message: str, code_n: int):
        super().__init__(message)
        self.message = message
        self.code_n = code_n


class RagCode(IntEnum):
    description: Optional[str]

    def __new__(cls, code_n: int, description: Optional[str]) -> "RagCode":
        obj = int.__new__(cls, code_n)
        obj._value_ = code_n
        obj.description = description
        return obj

    FeishuParseFailed = (
        1709900,
        "Feishu parse failed",
    )


class FeishuParseException(RagException):
    def __init__(self, message: str):
        super().__init__(message, code_n=RagCode.FeishuParseFailed)
