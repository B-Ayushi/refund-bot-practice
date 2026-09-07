import re

from instructions_loader import load_instruction
from tools.order_tools import get_order_status

STATUS_INSTRUCTIONS = load_instruction("status")


def order_status(state):
    order_id = re.search(r"\b\d+\b", state["user_query"])
    result = get_order_status(order_id.group(0)) if order_id else "Order ID not provided"
    return {
        "result": result
    }