from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel

class MemoryRecord(BaseModel):
    key: str
    value: Any
    source: Literal["user_explicit", "inferred"] = "user_explicit"
    confidence: float = 1.0
    updated_at: datetime = datetime.now(timezone.utc)
    expires_at: datetime | None = None
