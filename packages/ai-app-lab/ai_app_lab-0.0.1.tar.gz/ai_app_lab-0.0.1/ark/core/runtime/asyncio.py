import abc
import json
import logging
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Callable,
    Coroutine,
    Generic,
    List,
    Type,
    Union,
)

from pydantic import BaseModel, ValidationError
from volcenginesdkarkruntime._exceptions import ArkAPIError

import ark.core.utils.errorsv3 as errors_v3
from ark.core.idl.common_protocol import ArkError, RequestType, Response, ResponseType
from ark.core.idl.maas_protocol import MaasChatChoice, MaasChatRequest, MaasChatResponse
from ark.core.utils.context import get_reqid
from ark.core.utils.errors import GPTException, InternalServiceError
from ark.core.utils.types import parse_pydantic_error


class AsyncRunner(BaseModel, Generic[RequestType, ResponseType]):
    invoke: Callable[[RequestType], Coroutine[Any, Any, AsyncIterable[ResponseType]]]

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        runnable_func: Callable[[RequestType], AsyncIterable[ResponseType]],
        **kwargs: Any,
    ):
        async def handler(
            request: RequestType,
        ) -> AsyncIterable[ResponseType]:
            return runnable_func(request)

        super().__init__(invoke=handler, **kwargs)

    @abc.abstractmethod
    async def arun(self, request: RequestType) -> ResponseType:
        pass

    @abc.abstractmethod
    def astream(self, request: RequestType) -> AsyncIterator[str]:
        pass


class ChatAsyncRunner(AsyncRunner[MaasChatRequest, MaasChatResponse]):
    async def arun(self, request: MaasChatRequest) -> MaasChatResponse:  # type: ignore
        verbose: List[List[MaasChatChoice]] = []
        responses: List[MaasChatResponse] = []
        try:
            async for resp in await self.invoke(request):  # type: MaasChatResponse
                if resp.choices and resp.choices[0].message:
                    responses.append(resp)
                else:
                    verbose.append(resp.choices)
        except GPTException as e:
            resp = MaasChatResponse(req_id=get_reqid(), error=e.to_error())
            responses.append(resp)
            logging.exception("assistant chat meet gpt error")
        except Exception as e:
            err = InternalServiceError(str(e))
            resp = MaasChatResponse(req_id=get_reqid(), error=err.to_error())
            responses.append(resp)
            logging.exception("assistant chat meet internal error")

        response = MaasChatResponse.merge(responses=responses)
        return response

    async def astream(self, request: MaasChatRequest) -> AsyncIterator[str]:  # type: ignore
        try:
            async for resp in await self.invoke(request):  # type: MaasChatResponse
                if resp.choices and resp.choices[0].message:
                    if isinstance(resp, BaseModel):
                        yield f"data:{resp.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
                    else:
                        yield f"data:{json.dumps(resp, ensure_ascii=False)}\r\n\r\n"  # noqa E501
        except GPTException as e:
            resp = MaasChatResponse(req_id=get_reqid(), error=e.to_error())
            logging.exception("stream chat meet error")
            yield f"data:{resp.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
        except Exception as e:
            err = InternalServiceError(str(e))
            resp = MaasChatResponse(req_id=get_reqid(), error=err.to_error())
            logging.exception("stream chat meet error")
            yield f"data:{resp.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
        yield "data:[DONE]\r\n\r\n"


class CustomAsyncRunner(AsyncRunner[RequestType, ResponseType]):
    response_cls: Type[ResponseType]

    def __init__(
        self,
        response_cls: Type[ResponseType],
        runnable_func: Callable[[RequestType], AsyncIterable[ResponseType]],
        **kwargs: Any,
    ):
        super().__init__(
            response_cls=response_cls, runnable_func=runnable_func, **kwargs
        )

    async def arun(self, request: RequestType) -> ResponseType:  # type: ignore
        try:
            async for resp in await self.invoke(request):  # type: ResponseType
                return resp
        except GPTException as e:
            resp = self.response_cls(error=e.to_error())
            logging.error(f"bot meet error{e}")
            return resp
        except Exception as e:
            err = InternalServiceError(str(e))
            resp = self.response_cls(error=err.to_error())
            logging.error(f"bot meet internal error{err}")
            return resp

    async def astream(self, request: RequestType) -> AsyncIterator[str]:  # type: ignore
        try:
            async for resp in await self.invoke(request):  # type: ResponseType
                if isinstance(resp, BaseModel):
                    yield f"data:{resp.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
                else:
                    yield f"data:{json.dumps(resp, ensure_ascii=False)}\r\n\r\n"  # noqa E501
        except GPTException as e:
            resp = self.response_cls(error=e.to_error())
            logging.error("stream chat meet error")
            yield f"data:{resp.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
        except Exception as e:
            err = InternalServiceError(str(e))
            resp = self.response_cls(error=err.to_error())
            logging.error("stream chat meet error")
            yield f"data:{resp.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
        yield "data:[DONE]\r\n\r\n"


class ChatV3AsyncRunner(AsyncRunner[RequestType, ResponseType]):
    async def arun(self, request: RequestType) -> Union[Response, ResponseType]:  # type: ignore
        try:
            async for resp in await self.invoke(request):  # type: ResponseType
                return resp
        except errors_v3.APIException as e:
            logging.error(f"[API Error]: chat meet error:{e}")
            raise e
        except ValidationError as e:
            logging.error(f"[Validation Error]: chat meet parameter error:{e}")
            raise parse_pydantic_error(e)
        except ArkAPIError as e:
            logging.error(f"[Calling Chat Error]: chat meet error:{e}")
            raise e
        except Exception as e:
            err = errors_v3.InternalServiceError(str(e))
            logging.error(f"[Internal Error]: chat meet error:{e}")
            raise err

    async def astream(self, request: RequestType) -> AsyncIterator[str]:
        try:
            async for resp in await self.invoke(request):  # type: ResponseType
                yield f"data:{resp.model_dump_json(exclude_none=True)}\r\n\r\n"  # noqa E501
        except errors_v3.APIException as e:
            err = Response(error=e.to_error())
            logging.error(f"[API Error]: stream chat meet error:{e}")
            yield f"data:{err.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
        except ValidationError as e:
            err = Response(error=parse_pydantic_error(e).to_error())
            logging.error(f"[Validation Error]: stream chat meet parameter error:{e}")
            yield f"data:{err.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
        except ArkAPIError as e:
            err = Response(
                error=ArkError(
                    code=e.code or "",  # code is none when calling top failed
                    message=e.message or "",
                    type=e.type,
                    param=e.param,
                )
            )
            logging.error(f"[Calling Chat Error]: stream chat meet error:{e}")
            yield f"data:{err.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
        except Exception as e:
            err = Response(error=errors_v3.InternalServiceError(str(e)).to_error())
            logging.error(f"[Internal Error]: stream chat meet error:{e}")
            yield f"data:{err.model_dump_json(exclude_unset=True, exclude_none=True)}\r\n\r\n"  # noqa E501
        yield "data:[DONE]\r\n\r\n"
