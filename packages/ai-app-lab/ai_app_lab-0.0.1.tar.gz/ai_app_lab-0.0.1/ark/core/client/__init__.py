from typing import Any, Dict, Tuple, Type

from ark.core.client.action import ArkActionClient
from ark.core.client.authorization import APIGAuthorization, ArkAuthorization
from ark.core.client.base import Client, ClientPool, get_client_pool
from ark.core.client.maas import ArkClient
from ark.core.client.sse import AsyncSSEDecoder

__all__ = [
    "Client",
    "ClientPool",
    "ArkClient",
    "ArkActionClient",
    "ArkAuthorization",
    "APIGAuthorization",
    "AsyncSSEDecoder",
    "get_client_pool",
    "get_default_client_configs",
]


def get_default_client_configs() -> Dict[str, Tuple[Type[Client], Any]]:
    return {
        "chat": (
            ArkClient,
            {
                "host": "maas-api.ml-platform-cn-beijing.volces.com",
                "region": "cn-beijing",
            },
        ),
    }
