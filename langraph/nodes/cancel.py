from instructions_loader import load_instruction

CANCEL_INSTRUCTIONS = load_instruction("cancel")


def cancel_node(state):
	return {"result": "Cancellation request received"}
