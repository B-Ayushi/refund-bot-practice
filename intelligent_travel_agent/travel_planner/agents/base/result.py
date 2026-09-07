from pydantic import BaseModel

class ValidationDecision(BaseModel):
    status: str
    reason: str | None = None
