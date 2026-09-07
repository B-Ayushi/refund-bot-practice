from typing import Literal
from .common import AgentEnvelope

class ReviewResult(AgentEnvelope):
    schema_version: str = "review_result.v1"
    status: Literal["approve", "request_revision"]
    findings: list[str] = []
    budget_check: str
    completeness_check: str
    weather_checked: bool
    revision_instructions: list[str] = []
