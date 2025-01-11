import asyncio
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Coroutine,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from ark.core.idl.common_protocol import ChatResponse


def merge_response(response: Iterator[ChatResponse]) -> Optional[ChatResponse]:
    if response is None:
        return None
    merged = ChatResponse.merge([i for i in response])
    return merged


def async_iterator_to_sync(loop: asyncio.AbstractEventLoop, gen: Any) -> Iterator[Any]:
    try:
        while True:
            i = asyncio.run_coroutine_threadsafe(gen.__anext__(), loop).result()
            yield i
    except StopAsyncIteration:
        pass


T = TypeVar("T")


def sync_iterator_to_async(
    loop: asyncio.AbstractEventLoop, gen: Iterator[T], _END: Any = None
) -> AsyncIterable[Any]:
    if _END is None:
        _END = object()

        def wrap(gen: Iterator[T]) -> Iterator[T]:
            yield from gen
            yield _END

        gen = wrap(gen)

    async def async_gen(
        loop: asyncio.AbstractEventLoop, gen: Iterator[T]
    ) -> AsyncIterable[T]:
        while True:
            i: T = await loop.run_in_executor(None, next, gen)
            if i is _END:
                break
            yield i

    return async_gen(loop, gen)


async def async_any(coroutines: Any) -> bool:
    done = asyncio.as_completed(coroutines)
    for task in done:
        if await task:
            return True
    return False


async def aenumerate(
    asequence: AsyncIterable[T], start: int = 0
) -> AsyncIterator[Tuple[int, T]]:
    """Asynchronously enumerate an async iterator from a given start value"""
    n = start
    async for elem in asequence:
        yield n, elem
        n += 1


async def anext(asequence: AsyncIterator[T]) -> T:
    """
    Asynchronously get next item from async generator
    Note: python3.10 has a anext builtin function
    """
    return await asequence.__anext__()


async def gather(*coros_or_futures: Coroutine) -> List[Any]:
    tasks: List[asyncio.Task[Any]] = [
        asyncio.create_task(coro=task) for task in coros_or_futures
    ]
    try:
        results = await asyncio.gather(*tasks)
    except Exception:
        for task in tasks:
            task.cancel()
        raise
    else:
        return results
