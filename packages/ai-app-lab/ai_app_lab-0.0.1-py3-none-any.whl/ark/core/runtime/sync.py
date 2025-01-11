import abc
import json
import logging
from typing import Any, Callable, Iterable, List, TypeVar

from pydantic import BaseModel

from ark.core.idl.common_protocol import Request, Response
from ark.core.idl.maas_protocol import MaasChatChoice, MaasChatRequest, MaasChatResponse
from ark.core.task import task
from ark.core.utils.context import get_reqid
from ark.core.utils.errors import GPTException, InternalServiceError

RequestType = TypeVar("RequestType", bound=Request)
ResponseType = TypeVar("ResponseType", bound=Response)


class SyncRunner(BaseModel):
    invoke: Callable[[RequestType], Iterable[ResponseType]]

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        runnable_func: Callable[[RequestType], Iterable[ResponseType]],
        **kwargs: Any,
    ):
        super().__init__(invoke=runnable_func, **kwargs)

    @abc.abstractmethod
    def run(self, request: RequestType) -> Response:
        pass

    @abc.abstractmethod
    def generate(self, request: RequestType) -> Iterable[str]:
        pass


class ChatSyncRunner(SyncRunner):
    def __init__(
        self,
        runnable_func: Callable[[MaasChatRequest], Iterable[MaasChatResponse]],
        **kwargs: Any,
    ):
        super().__init__(runnable_func=runnable_func, **kwargs)

    @task(distributed=False)
    def run(self, request: MaasChatRequest) -> MaasChatResponse:
        verbose: List[List[MaasChatChoice]] = []
        responses: List[MaasChatResponse] = []

        try:
            for resp in self.invoke(request):  # type: MaasChatResponse
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

    @task(distributed=False)
    def generate(self, request: MaasChatRequest) -> Iterable[str]:
        try:
            for resp in self.invoke(request):  # type: MaasChatResponse
                if resp.choices and resp.choices[0].message:
                    if isinstance(resp, BaseModel):
                        yield f"data:{json.dumps(resp.model_dump(exclude_unset=True), ensure_ascii=False)}\r\n\r\n"  # noqa E501
                    else:
                        yield f"data:{resp}\r\n\r\n"  # noqa E501
        except GPTException as e:
            resp = MaasChatResponse(req_id=get_reqid(), error=e.to_error())
            logging.exception("stream chat meet error")
            yield f"data:{json.dumps(resp.model_dump(exclude_unset=True), ensure_ascii=False)}\r\n\r\n"  # noqa E501
        except Exception as e:
            err = InternalServiceError(str(e))
            resp = MaasChatResponse(req_id=get_reqid(), error=err.to_error())
            logging.exception("stream chat meet error")
            yield f"data:{json.dumps(resp.model_dump(exclude_unset=True), ensure_ascii=False)}\r\n\r\n"  # noqa E501
        yield "data:[DONE]\r\n\r\n"
