from app.agents.reasoning_agent import ReasoningAgent
from app.core.model_router import ModelRouter


def test_reasoning_agent_identifies_leave_intent():
    agent = ReasoningAgent()
    result = agent.classify_intent("I want to apply for casual leave next Monday and Tuesday")
    assert result == "apply_leave"


def test_model_router_routes_simple_task_to_small_model():
    router = ModelRouter()
    decision = router.route("I need to check my payroll status")
    assert decision["model_size"] == "small"


def test_model_router_routes_complex_task_to_large_model():
    router = ModelRouter()
    decision = router.route("This is a payroll dispute over 80,000 and involves a termination request")
    assert decision["model_size"] == "large"


def test_reasoning_agent_handles_employee_lookup_with_llm_style_prompting():
    agent = ReasoningAgent()
    result = agent.reason("show me the details of emp xyz")
    assert result["intent"] == "view_employee_profile"
    assert result["context"]["target_employee_id"] == "XYZ"
    assert "guardrails" in result
