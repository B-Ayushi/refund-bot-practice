from datetime import datetime, timezone
from pydantic import BaseModel

class WorkflowEvent(BaseModel):
    event: str
    request_id: str
    stage: str
    status: str
    timestamp: datetime = datetime.now(timezone.utc)
    metadata: dict[str, str] = {}
