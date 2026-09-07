from instructions_loader import load_instruction

REFUND_INSTRUCTIONS = load_instruction("refund")


def refund_node(state):
	return {"result": "Refund request received"}
