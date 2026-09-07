from typing import Literal
from pydantic import Field
from .common import AgentEnvelope

class GuardrailResult(AgentEnvelope):
    schema_version: str = "guardrail_result.v1"
    status: Literal["pass", "fail"]
    risk_score: float = Field(ge=0, le=1)
    confidence: float = Field(default=0.0, ge=0, le=1)
    signals: list[str] = Field(default_factory=list)
    user_message: str | None = None
    intent: str = "UNKNOWN"
    reason: str = ""
