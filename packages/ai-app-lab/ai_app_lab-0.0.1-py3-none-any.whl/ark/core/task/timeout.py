import asyncio
from typing import Any, AsyncIterable, Optional


class AsyncTimedIterable:
    def __init__(
        self,
        iterable: AsyncIterable[Any],
        timeout: Optional[int] = None,
        sentinel: Optional[Any] = None,
    ):
        class AsyncTimedIterator:
            def __init__(self) -> None:
                self._iterator = iterable.__aiter__()

            async def __anext__(self) -> Any:
                try:
                    return await asyncio.wait_for(self._iterator.__anext__(), timeout)
                except asyncio.TimeoutError as e:
                    if sentinel:
                        raise sentinel
                    else:
                        raise e

        self._factory = AsyncTimedIterator

    def __aiter__(self) -> Any:
        return self._factory()
