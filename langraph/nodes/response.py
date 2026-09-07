from instructions_loader import load_instruction

RESPONSE_INSTRUCTIONS = load_instruction("response")


def response_node(state):
	if state.get("intent") == "blocked" or not state.get("input_allowed", True):
		return {"result": "I can only help with order status, cancellations, refunds, and related order questions."}
	return {"result": state.get("result", "Please contact support for help with that request")}
