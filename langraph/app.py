from langgraph.graph import END, START, StateGraph

from guardrails.input_guardrails.checks import (
    input_guardrail,
    intent_guardrail,
    route_input,
)

from guardrails.output_guardrails.checks import (
    output_guardrail,
)

from nodes.cancel import cancel_node
from nodes.intent import detect_intent, route_intent
from nodes.refund import refund_node
from nodes.response import response_node
from nodes.status import order_status

from state import AgentState


builder = StateGraph(AgentState)

# Nodes
builder.add_node("input_guardrail", input_guardrail)
builder.add_node("intent", detect_intent)
builder.add_node("intent_guardrail", intent_guardrail)
builder.add_node("refund", refund_node)
builder.add_node("cancel", cancel_node)
builder.add_node("status", order_status)
builder.add_node("response", response_node)
builder.add_node("output_guardrail", output_guardrail)

# START -> input guardrail
builder.add_edge(START, "input_guardrail")

# Input guardrail routing
builder.add_conditional_edges(
    "input_guardrail",
    route_input,
    {
        "allowed": "intent",
        "blocked": "response",
    },
)

# Intent detection
builder.add_edge("intent", "intent_guardrail")

# Intent routing
builder.add_conditional_edges(
    "intent_guardrail",
    route_intent,
    {
        "refund": "refund",
        "cancel": "cancel",
        "status": "status",
        "faq": "response",
        "blocked": "response",
    },
)

# Business flow
builder.add_edge("refund", "response")
builder.add_edge("cancel", "response")
builder.add_edge("status", "response")

# Always run output guardrail
builder.add_edge("response", "output_guardrail")

# End
builder.add_edge("output_guardrail", END)

graph = builder.compile()


if __name__ == "__main__":
    user_query = input("How can I help you? ")

    result = graph.invoke(
        {
            "user_query": user_query
        }
    )

    print(result["result"])