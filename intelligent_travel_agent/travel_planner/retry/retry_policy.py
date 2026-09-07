import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

async def retry_async(operation: Callable[[], Awaitable[T]], attempts: int = 3, base_delay: float = 0.01) -> T:
    for attempt in range(attempts):
        try:
            return await operation()
        except Exception:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(base_delay * (2 ** attempt))
    raise RuntimeError("unreachable")
