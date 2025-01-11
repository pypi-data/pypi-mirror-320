"errors"

import logging
from enum import Enum
from typing import Optional, Union

from volcenginesdkarkruntime._exceptions import (
    ArkAPITimeoutError,
    ArkRateLimitError,
)

from ark.core.idl.common_protocol import ArkError
from ark.core.utils import context


class ReprEnum(Enum):
    """
    Only changes the repr(), leaving str() and format() to the mixed-in type.
    """


class StrEnum(str, ReprEnum):
    """
    Enum where members are also (and must be) strings
    """

    def __new__(cls, *values: str) -> "StrEnum":
        "values must already be of type `str`"
        if len(values) > 3:
            raise TypeError("too many arguments for str(): %r" % (values,))
        if len(values) == 1:
            # it must be a string
            if not isinstance(values[0], str):
                raise TypeError("%r is not a string" % (values[0],))
        if len(values) >= 2:
            # check that encoding argument is a string
            if not isinstance(values[1], str):
                raise TypeError("encoding must be a string, not %r" % (values[1],))
        if len(values) == 3:
            # check that errors argument is a string
            if not isinstance(values[2], str):
                raise TypeError("errors must be a string, not %r" % (values[2]))
        value = str(*values)
        member = str.__new__(cls, value)
        member._value_ = value
        return member

    def _generate_next_value_(self, start, count, last_values) -> str:  # type: ignore
        """
        Return the lower-cased version of the member name.
        """
        return self.lower()


class ErrorCode(StrEnum):
    http_code: int
    message: str
    error_type: str

    def __new__(
        cls,
        code: str,
        http_code: int,
        message: Optional[str] = None,
        error_type: Optional[str] = None,
    ) -> "ErrorCode":
        error_code = str.__new__(cls, code)
        error_code._value_ = code
        error_code.http_code = http_code  # type: ignore
        error_code.message = message or ""  # type: ignore
        error_code.error_type = error_type or ""  # type: ignore
        return error_code

    MissingParameter = (
        "MissingParameter",
        400,
        "The request failed because it is missing required parameters",
        "BadRequest",
    )
    InvalidParameter = (
        "InvalidParameter",
        400,
        "A parameter specified in the request is not valid: {parameter}",
        "BadRequest",
    )
    InvalidAction = (
        "InvalidAction",
        400,
        "The request targeted action that does not exist or is invalid.",
        "BadRequest",
    )
    InvalidBot = (
        "InvalidBot",
        400,
        "The request targeted bot that does not exist or is invalid.",
        "BadRequest",
    )
    ResourceNotFound = (
        "ResourceNotFound",
        404,
        "The specified resource is not found",
        "NotFound",
    )
    RateLimitExceeded = (
        "RateLimitExceeded",
        429,
        "The Requests Per Minute(RPM) limit of the associated {resource_type} for your "
        "account has been exceeded.",
        "TooManyRequests",
    )
    ServerOverloaded = (
        "ServerOverloaded",
        429,
        "The service: {service} is currently unable to handle "
        "additional requests due to server overload.",
        "TooManyRequests",
    )

    SensitiveContentDetected = (
        "SensitiveContentDetected",
        400,
        "The request failed because the input text may contain sensitive information.",
        "BadRequest",
    )

    AuthenticationError = (
        "AuthenticationError",
        401,
        "The API key in the request is missing or invalid.",
        "Unauthorized",
    )

    AccessDenied = (
        "AccessDenied",
        403,
        "The request failed because you do not have access to the requested resource.",
        "Forbidden",
    )

    AccountOverdueError = (
        "AccountOverdueError",
        403,
        "The request failed because your account has an overdue balance.",
        "Forbidden",
    )
    QuotaExceeded = (
        "QuotaExceeded",
        429,
        "Your account {account_id} has exhausted its free trial "
        "quota for {resource_type}.",
        "TooManyRequests",
    )

    InternalServiceError = (
        "InternalServiceError",
        500,
        "The service encountered an unexpected internal error.",
        "InternalServerError",
    )

    Unknown = ("Unknown", 500, "Unknown error")

    ModelLoadingError = (
        "ModelLoadingError",
        429,
        "The request cannot be processed at this time because "
        "the model is currently being loaded",
        "TooManyRequests",
    )

    KnowledgeBaseError = (
        "KnowledgeBaseError",
        500,
        "Retrieving knowledgebase meet error",
        "InternalServerError",
    )

    LinkReaderBaseError = (
        "LinkReaderBaseError",
        500,
        "Reading links meet error",
        "InternalServerError",
    )

    APITimeoutError = (
        "APITimeoutError",
        500,
        "Request timed out",
        "InternalServerError",
    )


class APIException(Exception):
    def __init__(
        self,
        message: str,
        code: Union[ErrorCode, str],
        parameter: Optional[str] = None,
        http_code: Optional[int] = 500,
        error_type: Optional[str] = "InternalServerError",
    ):
        super().__init__(message)
        self.message = f"{message} Request id: {context.get_reqid()}"
        self.resource_id = context.get_resource_id()
        self.account_id = context.get_account_id() or ""
        self.code = code.value if isinstance(code, ErrorCode) else str(code)
        self.http_code = (
            code.http_code if isinstance(code, ErrorCode) else (http_code or 500)
        )
        self.type = (
            code.error_type
            if isinstance(code, ErrorCode)
            else (error_type or "InternalServerError")
        )
        self.parameter = parameter

    def __str__(self) -> str:
        return (
            "Detailed exception information is listed below.\n"
            + "account_id: {}\n"
            + "resource_id: {}\n"
            + "code: {}\n"
            + "message: {}"
        ).format(self.account_id, self.resource_id, self.code, self.message)

    def to_error(self) -> ArkError:
        return ArkError(
            code=self.code, message=self.message, param=self.parameter, type=self.type
        )


class InternalServiceError(APIException):
    def __init__(self, message: str):
        logging.error(f"[Internal Error]: {message}")
        super().__init__(
            message=ErrorCode.InternalServiceError.message,
            code=ErrorCode.InternalServiceError,
        )


class InvalidParameter(APIException):
    def __init__(self, parameter: str, cause: Optional[str] = None):
        message = ErrorCode.InvalidParameter.message.format(parameter=parameter)
        if cause:
            message = f"{message}.{cause}"
        super().__init__(
            message=message, code=ErrorCode.InvalidParameter, parameter=parameter
        )


class InvalidAction(APIException):
    def __init__(self, parameter: Optional[str] = None):
        message = ErrorCode.InvalidAction.message
        super().__init__(
            message=message, code=ErrorCode.InvalidAction, parameter=parameter
        )


class InvalidBot(APIException):
    def __init__(self, parameter: Optional[str] = None):
        message = ErrorCode.InvalidBot.message
        super().__init__(
            message=message, code=ErrorCode.InvalidBot, parameter=parameter
        )


class MissingParameter(APIException):
    def __init__(self, parameter: Optional[str] = None):
        message = (
            f"{ErrorCode.MissingParameter.message}:{parameter}"
            if parameter
            else str(ErrorCode.MissingParameter.message)
        )
        super().__init__(
            message=message, code=ErrorCode.MissingParameter, parameter=parameter
        )


class ResourceNotFound(APIException):
    def __init__(self, resource_type: Optional[str] = None):
        message = (
            f"{ErrorCode.ResourceNotFound.message}:{resource_type}"
            if resource_type
            else str(ErrorCode.ResourceNotFound.message)
        )
        super().__init__(
            message,
            code=ErrorCode.ResourceNotFound,
            parameter=resource_type,
        )


class RateLimitExceeded(APIException):
    def __init__(self, resource_type: str):
        message = ErrorCode.RateLimitExceeded.message.format(
            resource_type=resource_type
        )
        super().__init__(
            message,
            code=ErrorCode.RateLimitExceeded,
            parameter=resource_type,
        )


class ServerOverloaded(APIException):
    def __init__(self, service: str):
        message = ErrorCode.ServerOverloaded.message.format(service=service)
        super().__init__(
            message,
            code=ErrorCode.ServerOverloaded,
            parameter=service,
        )


class AuthenticationError(APIException):
    def __init__(self, cause: Optional[str] = None):
        message = ErrorCode.AuthenticationError.message
        if cause:
            message = f"{message} {cause}"
        super().__init__(
            message=message,
            code=ErrorCode.AuthenticationError,
        )


class AccessDenied(APIException):
    def __init__(self, cause: Optional[str] = None):
        message = ErrorCode.AccessDenied.message
        if cause:
            message = f"{message}.{cause}"
        super().__init__(
            message,
            code=ErrorCode.AccessDenied,
        )


class QuotaExceeded(APIException):
    def __init__(self, account_id: str, resource_type: str):
        message = ErrorCode.QuotaExceeded.message.format(
            account_id=account_id, resource_type=resource_type
        )
        super().__init__(message, code=ErrorCode.QuotaExceeded, parameter=resource_type)


class SensitiveContentDetected(APIException):
    def __init__(self, message: str):
        super().__init__(message, code=ErrorCode.SensitiveContentDetected)


class AccountOverdueError(APIException):
    def __init__(self, message: str):
        super().__init__(message, code=ErrorCode.AccountOverdueError)


class KnowledgeBaseError(APIException):
    def __init__(self, message: str):
        super().__init__(message, code=ErrorCode.KnowledgeBaseError)


class LinkReaderBaseError(APIException):
    def __init__(self, message: str):
        super().__init__(message, code=ErrorCode.LinkReaderBaseError)


class APITimeoutError(APIException):
    def __init__(self, message: str):
        logging.error(f"[API timeout error]: {message}")
        super().__init__(
            message=ErrorCode.APITimeoutError.message,
            code=ErrorCode.APITimeoutError,
        )


FALLBACK_EXCEPTIONS = (
    APITimeoutError,
    ArkAPITimeoutError,
    RateLimitExceeded,
    ArkRateLimitError,
)
