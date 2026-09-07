from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

async def with_fallback(primary: Callable[[], Awaitable[T]], backup: Callable[[], Awaitable[T]]) -> T:
    try:
        return await primary()
    except Exception:
        return await backup()
