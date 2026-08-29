from __future__ import annotations


class ModelRouter:
    """Routes tasks to small or large models based on complexity and safety needs."""

    def route(self, message: str) -> dict:
        lower = message.lower()

        complex_indicators = [
            "dispute",
            "harassment",
            "termination",
            "policy conflict",
            "salary dispute",
            "raise",
            "escalate",
            "multiple policies",
            "urgent legal",
        ]

        if any(indicator in lower for indicator in complex_indicators):
            return {
                "model_size": "large",
                "reason": "High-risk or ambiguous workflow requires stronger reasoning and safeguards.",
            }

        return {
            "model_size": "small",
            "reason": "Simple intent classification and routine workflow execution can use a lighter model.",
        }
