from app.agents.escalation_agent import EscalationAgent
from app.agents.execution_agent import ExecutionAgent
from app.agents.intent_agent import IntentAgent
from app.agents.policy_agent import PolicyAgent
from app.agents.reasoning_agent import ReasoningAgent
from app.core.mcp_router import MCPRouter
from app.core.rbac import RBAC
from app.core.security import validate_request
from app.memory.session_store import InMemorySessionStore


class Orchestrator:
    def __init__(self) -> None:
        self.intent_agent = IntentAgent()
        self.reasoning_agent = ReasoningAgent()
        self.policy_agent = PolicyAgent()
        self.execution_agent = ExecutionAgent()
        self.escalation_agent = EscalationAgent()
        self.mcp_router = MCPRouter()
        self.rbac = RBAC()
        self.session_store = InMemorySessionStore()

    def process(self, employee_id: str, message: str, target_employee_id: str | None = None, role: str = "employee") -> dict:
        validate_request(message, employee_id, target_employee_id)
        self.session_store.add_message(employee_id, message)

        reasoning = self.reasoning_agent.reason(message)
        
        # If Groq security check blocked the request, return blocked status immediately
        if reasoning.get("intent") == "blocked":
            return {
                "status": "blocked",
                "intent": "blocked",
                "reasoning": reasoning,
                "result": {
                    "message": f"Security violation: {reasoning.get('blocked_reason', 'Suspicious request detected')}",
                    "action": "Request rejected and logged",
                },
            }
        
        route_decision = self.mcp_router.route_task(message)
        intent = reasoning["intent"]
        policy = self.policy_agent.evaluate(intent, message)

        action_map = {
            "apply_leave": "request_leave",
            "check_payroll_status": "view_own_payroll",
            "create_reimbursement_ticket": "request_reimbursement",
            "generate_verification_letter": "generate_verification_letter",
            "view_employee_profile": "view_own_profile",
            "transfer_request": "request_transfer",
            "exit_request": "submit_exit_request",
        }
        if reasoning.get("context", {}).get("target_employee_id"):
            requested_target = reasoning["context"]["target_employee_id"]
            if target_employee_id is None:
                target_employee_id = requested_target

        action = action_map.get(intent, "view_own_profile")
        is_authorized = self.rbac.authorize(role, action) and self.rbac.can_access_employee_data(role, employee_id, target_employee_id)

        if not is_authorized:
            return {
                "status": "forbidden",
                "intent": intent,
                "reasoning": reasoning,
                "route": route_decision,
                "result": {
                    "message": "Action not authorized for this role or employee scope.",
                    "required_role": "hr_admin or appropriate manager",
                },
                "policy": policy,
                "rbac": {"role": role, "action": action, "authorized": False},
            }

        if not policy["allowed"] or policy.get("escalate"):
            escalated = self.escalation_agent.escalate(policy["reason"], employee_id)
            return {
                "status": "escalated",
                "intent": intent,
                "reasoning": reasoning,
                "route": route_decision,
                "result": escalated,
                "policy": policy,
                "rbac": {"role": role, "action": action, "authorized": True},
            }

        result = self.execution_agent.execute(intent, employee_id, message)
        self.session_store.update_context(employee_id, "last_intent", intent)
        return {
            "status": "success",
            "intent": intent,
            "reasoning": reasoning,
            "route": route_decision,
            "result": result,
            "policy": policy,
            "rbac": {"role": role, "action": action, "authorized": True},
        }
