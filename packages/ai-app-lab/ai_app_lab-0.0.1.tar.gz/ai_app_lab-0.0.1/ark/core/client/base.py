import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from ark.core.task.task import task
from ark.core.utils.common import Singleton


class Client(Singleton):
    pass


class ClientPool(Singleton):
    _registry: Dict[str, Type[Client]] = {}
    clients: Dict[str, Client] = {}

    def __init__(
        self,
        clients: Dict[str, Tuple[Type[Client], Dict[str, Any]]],
    ) -> None:
        for name, (cls, config) in (clients or dict()).items():
            try:
                self.clients[name] = cls(**config)
            except Exception as e:
                logging.error(f"init client pool failed:{e}")
                continue

    def get_client_names(self) -> List[str]:
        return [name for name in self.clients.keys()]

    def get_client(self, name: str) -> Optional[Client]:
        return self.clients.get(name)

    @classmethod
    def register(
        cls, name: Optional[str] = None
    ) -> Callable[[Type[Client]], Type[Client]]:
        def func(wrapped_cls: Type[Client]) -> Type[Client]:
            if name:
                cls._registry[name] = wrapped_cls
            else:
                cls._registry[wrapped_cls.__name__] = wrapped_cls

            return wrapped_cls

        return func

    @classmethod
    async def async_get_client(cls, name: str, config: Dict[str, Any]) -> Client:
        if name not in cls.clients:
            cls.clients[name] = await cls.async_create_client(name, **config)

        return cls.clients[name]

    @classmethod
    async def async_create_client(cls, name: str, *args: Any, **kwargs: Any) -> Client:
        if name not in cls._registry:
            raise ValueError(f"Unknown client name: {name}")
        if not issubclass(cls._registry[name], Client):
            raise ValueError(f"{name} is not a subclass of client")
        client_cls = cls._registry[name]

        return await client_cls.get_instance_async(*args, **kwargs)


@task()
def get_client_pool(
    clients: Optional[Dict[str, Tuple[Type[Client], Any]]] = None,
) -> ClientPool:
    return ClientPool.get_instance_sync(clients=clients)
