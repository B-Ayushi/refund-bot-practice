from app.tools.hr_tools import HRToolService


class ExecutionAgent:
    def __init__(self, tool_service: HRToolService | None = None):
        self.tool_service = tool_service or HRToolService()

    def execute(self, intent: str, employee_id: str, message: str) -> dict:
        if intent == "apply_leave":
            return self.tool_service.apply_leave(employee_id, "2026-09-01", "2026-09-02", "casual")
        if intent == "check_payroll_status":
            return self.tool_service.get_payroll_status(employee_id)
        if intent == "generate_verification_letter":
            return self.tool_service.generate_verification_letter(employee_id)
        if intent == "create_reimbursement_ticket":
            return self.tool_service.create_reimbursement_ticket(employee_id, "medical")
        if intent == "view_employee_profile":
            return {
                "status": "profile_retrieved",
                "message": f"Employee profile for {employee_id} reviewed. Additional employee data access is gated by RBAC and target scope.",
                "employee_id": employee_id,
            }
        return {"status": "not_handled", "message": "No execution path available for this intent."}
