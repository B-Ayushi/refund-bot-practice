from typing import Literal
from pydantic import Field
from .common import AgentEnvelope

class PolicyResult(AgentEnvelope):
    schema_version: str = "policy_result.v1"
    status: Literal["pass", "fail"]
    reason_code: str | None = None
    user_message: str | None = None
    internal_reason: str | None = None
