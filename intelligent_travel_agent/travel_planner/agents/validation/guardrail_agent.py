from datetime import datetime, timezone
from travel_planner.agents.base.agent import Agent
from travel_planner.schemas.guardrail_result import GuardrailResult
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.guardrails.validators import detect_malicious
from travel_planner.agents.guardrails.intent_classifier import IntentClassifier

class GuardrailAgent(Agent[TravelRequest, GuardrailResult]):
    name = "guardrail"
    def __init__(self, classifier: IntentClassifier | None = None) -> None:
        self.classifier = classifier or IntentClassifier()

    async def run(self, request: TravelRequest) -> GuardrailResult:
        intent = await self.classifier.classify(request.model_dump_json())
        signals = detect_malicious(request.model_dump_json())
        blocked_intent = intent.intent != "TRAVEL_REQUEST"
        return GuardrailResult(
            request_id="", agent=self.name, created_at=datetime.now(timezone.utc),
            status="fail" if signals or blocked_intent else "pass",
            risk_score=1.0 if signals or blocked_intent else 0.0,
            confidence=intent.confidence,
            signals=signals + ([intent.intent] if blocked_intent else []),
            user_message="This request could not pass safety validation." if signals or blocked_intent else None,
            intent=intent.intent,
            reason=intent.reason,
        )
