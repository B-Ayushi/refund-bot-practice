import asyncio
from dataclasses import dataclass
from travel_planner.agents.validation.guardrail_agent import GuardrailAgent
from travel_planner.agents.validation.policy_agent import PolicyAgent
from travel_planner.agents.validation.weather_agent import WeatherAgent
from travel_planner.config.constants import MAX_VALIDATION_ITERATIONS
from travel_planner.schemas.guardrail_result import GuardrailResult
from travel_planner.schemas.policy_result import PolicyResult
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.schemas.weather_result import WeatherResult
from travel_planner.observability.logger import logger

@dataclass
class ValidationOutcome:
    status: str
    policy: PolicyResult
    guardrail: GuardrailResult
    weather: WeatherResult
    reason: str | None = None

class ValidationWorkflow:
    def __init__(self, policy: PolicyAgent | None = None, guardrail: GuardrailAgent | None = None, weather: WeatherAgent | None = None) -> None:
        self.policy = policy or PolicyAgent()
        self.guardrail = guardrail or GuardrailAgent()
        self.weather = weather or WeatherAgent()

    async def run(self, request: TravelRequest) -> ValidationOutcome:
        if not request.is_complete():
            raise ValueError("ValidationWorkflow requires a complete TravelRequest")
        for _ in range(MAX_VALIDATION_ITERATIONS):
            logger.event("workflow_transition", stage="validation_fan_out", status="started")
            policy, guardrail, weather = await asyncio.gather(
                self.policy.run(request), self.guardrail.run(request), self.weather.run(request)
            )
            if policy.status == "fail":
                logger.event("workflow_transition", stage="validation_decision", status="rejected_policy")
                return ValidationOutcome("rejected_policy", policy, guardrail, weather, policy.reason_code)
            if guardrail.status == "fail":
                logger.event("workflow_transition", stage="validation_decision", status="rejected_guardrail")
                return ValidationOutcome("rejected_guardrail", policy, guardrail, weather, "guardrail_failed")
            if weather.status == "warning":
                logger.event("workflow_transition", stage="validation_decision", status="weather_warning")
                return ValidationOutcome("weather_warning", policy, guardrail, weather, "acknowledgement_required")
            if weather.status == "degraded":
                logger.event("workflow_transition", stage="validation_decision", status="requires_provider")
                return ValidationOutcome("requires_provider", policy, guardrail, weather, "REQUIRES_PROVIDER: weather")
            logger.event("workflow_transition", stage="validation_decision", status="pass")
            return ValidationOutcome("pass", policy, guardrail, weather)
        raise RuntimeError("validation iteration limit reached")
