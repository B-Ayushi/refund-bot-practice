from travel_planner.guardrails.policy_rules import violates_policy
from travel_planner.guardrails.validators import detect_malicious
from travel_planner.agents.guardrails.intent_classifier import IntentClassifier

class InputGuardrails:
    def __init__(self, classifier: IntentClassifier | None = None) -> None:
        self.classifier = classifier or IntentClassifier()

    async def check(self, raw_text: str) -> tuple[bool, str | None]:
        intent = await self.classifier.classify(raw_text)
        if intent.intent != "TRAVEL_REQUEST":
            return False, f"GUARDRAIL_BLOCKED: {intent.intent}"
        if detect_malicious(raw_text):
            return False, "GUARDRAIL_BLOCKED"
        if violates_policy(raw_text):
            return False, "POLICY_BLOCKED"
        return True, None
