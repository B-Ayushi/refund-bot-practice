from datetime import datetime, timezone
from travel_planner.agents.base.agent import Agent
from travel_planner.schemas.policy_result import PolicyResult
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.guardrails.policy_rules import violates_policy

class PolicyAgent(Agent[TravelRequest, PolicyResult]):
    name = "policy"
    async def run(self, request: TravelRequest) -> PolicyResult:
        policy_text = request.model_dump_json()
        blocked = violates_policy(policy_text)
        return PolicyResult(
            request_id="", agent=self.name, created_at=datetime.now(timezone.utc),
            status="fail" if blocked else "pass",
            reason_code="POLICY_BLOCKED" if blocked else None,
            user_message="This travel request cannot be processed." if blocked else None,
        )
