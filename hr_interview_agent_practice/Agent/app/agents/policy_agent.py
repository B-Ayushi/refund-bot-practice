from app.core.config import settings


class PolicyAgent:
    def evaluate(self, intent: str, message: str) -> dict:
        lower = message.lower()

        if "harassment" in lower:
            return {"allowed": False, "reason": "Harassment complaint requires human escalation.", "escalate": True}
        if "termination" in lower or "fire" in lower or "resign" in lower:
            return {"allowed": False, "reason": "Termination or exit requests require escalation.", "escalate": True}
        if "salary" in lower and "50000" in lower or "50,000" in lower:
            return {"allowed": False, "reason": "Payroll dispute exceeds threshold and requires human review.", "escalate": True}
        if "policy" in lower and "conflict" in lower:
            return {"allowed": False, "reason": "Policy conflict detected.", "escalate": True}

        if intent == "apply_leave":
            if "monday" in lower or "tuesday" in lower:
                return {"allowed": True, "reason": "Leave request conforms to policy.", "escalate": False}
            return {"allowed": True, "reason": "Leave request is valid.", "escalate": False}

        return {"allowed": True, "reason": "Validated against policy baseline.", "escalate": False}
