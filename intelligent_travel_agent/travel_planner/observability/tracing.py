from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any
from .logger import logger

@asynccontextmanager
async def span(name: str, **metadata: Any) -> AsyncIterator[None]:
    logger.event("span_started", name=name, **metadata)
    try:
        yield
    finally:
        logger.event("span_finished", name=name, **metadata)
