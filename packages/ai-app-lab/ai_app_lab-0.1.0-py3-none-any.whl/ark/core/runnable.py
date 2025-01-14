from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Generic, Iterator, List, TypeVar

T = TypeVar("T")


class Runnable(Generic[T], ABC):
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def arun(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def stream(self, *args: Any, **kwargs: Any) -> Iterator[T]:
        raise NotImplementedError

    def astream(self, *args: Any, **kwargs: Any) -> AsyncIterator[T]:
        raise NotImplementedError

    def batch(self, *args: Any, **kwargs: Any) -> List[T]:
        raise NotImplementedError

    async def abatch(self, *args: Any, **kwargs: Any) -> List[T]:
        raise NotImplementedError
