class EscalationAgent:
    def escalate(self, reason: str, employee_id: str) -> dict:
        return {
            "status": "escalated",
            "employee_id": employee_id,
            "ticket": "HR-ESCALATION-001",
            "reason": reason,
            "message": "This request has been forwarded to the HR team for manual review.",
        }
