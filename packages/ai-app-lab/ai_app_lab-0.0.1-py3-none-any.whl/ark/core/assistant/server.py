import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Generic, Optional, Tuple, Type, Union

import fastapi
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from ark.core.assistant.middleware import LogIdMiddleware
from ark.core.client import Client, get_client_pool
from ark.core.idl.common_protocol import RequestType, ResponseType
from ark.core.idl.maas_protocol import MaasChatRequest
from ark.core.runtime.asyncio import AsyncRunner
from ark.core.utils.types import load_request


def _get_lock() -> asyncio.Lock:
    return asyncio.Lock()


def _default_endpoint_config() -> Dict[str, Type[MaasChatRequest]]:
    return {"/api/v2/assistant/chat": MaasChatRequest}


def _default_healthcheck_config() -> str:
    return "/healthz"


class AssistantServer(BaseModel, Generic[RequestType, ResponseType]):
    """AssistantServer in charge of the server router and runtime"""

    runner: AsyncRunner
    """ handler runtime of assistant server"""
    clients: Optional[Dict[str, Tuple[Type[Client], Dict[str, Any]]]]
    """
    configuration of client cls & input config
    format: {$client_name: ($cls, $config_dict) }
    """
    endpoint_config: Dict[str, Type[RequestType]] = Field(
        default_factory=_default_endpoint_config
    )
    """
    configuration of endpoint path & request class,
    format: {$ep_path: $request_cls }
    """
    health_check_path: str = Field(default_factory=_default_healthcheck_config)
    """path for server health check"""
    app: FastAPI
    """server application"""

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        runner: AsyncRunner,
        endpoint_config: Optional[Dict[str, Type[RequestType]]] = None,
        clients: Optional[Dict[str, Tuple[Type[Client], Dict[str, Any]]]] = None,
        app: Optional[FastAPI] = None,
        health_check_path: Optional[str] = None,
        **kwargs: Any,
    ):
        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncIterator[Dict[str, Any]]:
            yield {"client_pool": get_client_pool(clients)}

        super().__init__(
            runner=runner,
            endpoint_config=endpoint_config or _default_endpoint_config(),
            clients=clients,
            health_check_path=health_check_path or _default_healthcheck_config(),
            app=app or FastAPI(lifespan=lifespan),
            **kwargs,
        )

        self.add_middlewares(self.app)
        self.add_routes(self.app)

    async def handler(self, http_request: fastapi.Request) -> fastapi.Response:
        try:
            request: RequestType = await load_request(
                http_request=http_request,
                req_cls=self.get_request_cls(http_request.url.path),
            )

            if request.stream:
                generator = self.runner.astream(request)
                return StreamingResponse(generator, media_type="text/event-stream")
            else:
                return await self.runner.arun(request)

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")

    async def health_check(self) -> Any:
        return {}

    def add_routes(self, app: FastAPI) -> None:
        for endpoint_path, request_cls in self.endpoint_config.items():
            app.add_api_route(
                endpoint_path,
                self.handler,
                methods=["POST", "OPTIONS", "GET"],
            )
        app.add_api_route(
            self.health_check_path,
            self.health_check,
            methods=["GET"],
        )

    def get_request_cls(self, api_path: str) -> Type[RequestType]:
        assert api_path in self.endpoint_config, ValueError(
            "no corresponding api in endpoint configs"
        )
        return self.endpoint_config[api_path]

    @staticmethod
    def add_middlewares(app: FastAPI) -> None:
        app.add_middleware(LogIdMiddleware)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @staticmethod
    def run(
        app: Union[FastAPI, str],
        host: str = "0.0.0.0",
        port: int = 8080,
        workers_num: int = 1,
    ) -> None:
        uvicorn.run(app, host=host, port=port, workers=workers_num)
