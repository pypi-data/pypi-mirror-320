import asyncio
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Coroutine,
    List,
    Optional,
    Tuple,
    TypeVar,
)

T = TypeVar("T")


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
