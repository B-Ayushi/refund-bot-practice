from app.agents.orchestrator import Orchestrator


def test_leave_request_is_processed():
    orchestrator = Orchestrator()
    result = orchestrator.process("E123", "I want to apply for casual leave tomorrow")
    assert result["result"]["status"] == "approved"


def test_policy_escalates_hr_risk():
    orchestrator = Orchestrator()
    result = orchestrator.process("E123", "I want to file a harassment complaint")
    assert result["status"] == "escalated"
