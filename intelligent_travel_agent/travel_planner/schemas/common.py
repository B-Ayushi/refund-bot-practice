from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str

class Evidence(Contract):
    ref: str
    source: str
    retrieved_at: datetime

class AgentEnvelope(Contract):
    request_id: str
    agent: str
    created_at: datetime
    evidence_refs: list[str] = Field(default_factory=list)

class ErrorInfo(BaseModel):
    code: str
    message: str
    retryable: bool = False

Status = Literal["success", "degraded", "failed"]
