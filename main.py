from agents.intent_agent import IntentAgent
from agents.policy_agent import PolicyAgent
from agents.risk_agent import RiskAgent
from agents.execution_agent import ExecutionAgent
from agents.evaluation_agent import EvaluationAgent
from agents.routing_agent import RoutingAgent

from tools.order_tools import (
    get_order_details,
    get_refund_status
)

from guardrails.llm_guardrail import (
    classify_safety
)

from guardrails.output_guardrails import (
    validate_output
)

from human_review.human_review import (
    HumanReview
)

from evaluator.metrics import Metrics


# -------------------------
# Agent Initialization
# -------------------------

intent_agent = IntentAgent()
policy_agent = PolicyAgent()
risk_agent = RiskAgent()
execution_agent = ExecutionAgent()
evaluation_agent = EvaluationAgent()
routing_agent = RoutingAgent()
human_review = HumanReview()

metrics = Metrics()


# -------------------------
# Main Loop
# -------------------------

while True:

    query = input(
        "\nEnter query (exit to quit): "
    ).strip()

    # -------------------------
    # Empty Query Check
    # -------------------------

    if not query:

        print(
            "Please enter a valid query."
        )

        continue

    # -------------------------
    # Exit Condition
    # -------------------------

    if query.lower() == "exit":

        break

    metrics.total_requests += 1


    # =====================================================
    # LLM SAFETY GUARDRAIL
    # =====================================================

    safety_result = classify_safety(
        query
    )

    category = safety_result.get(
        "category",
        "UNSAFE"
    )

    confidence = safety_result.get(
        "confidence",
        0.0
    )

    print(
        f"[Safety Check] {category} "
        f"(confidence={confidence})"
    )


    # -------------------------
    # Prompt Injection
    # -------------------------

    if category == "PROMPT_INJECTION":

        print(
            "Blocked: Prompt Injection detected."
        )

        metrics.rejected += 1

        continue


    # -------------------------
    # Jailbreak
    # -------------------------

    if category == "JAILBREAK":

        print(
            "Blocked: Jailbreak attempt detected."
        )

        metrics.rejected += 1

        continue


    # -------------------------
    # Threat
    # -------------------------

    if category == "THREAT":

        print(
            "Threatening language detected."
        )

        print(
            "Escalating this conversation "
            "to human support."
        )

        metrics.escalated += 1

        continue


    # -------------------------
    # Harassment
    # -------------------------

    if category == "HARASSMENT":

        print(
            "I can help with your request, "
            "but please keep the conversation respectful."
        )

        continue


    # -------------------------
    # Illegal Request
    # -------------------------

    if category == "ILLEGAL_REQUEST":

        print(
            "I cannot assist with that request."
        )

        metrics.rejected += 1

        continue


    # -------------------------
    # PII Request
    # -------------------------

    if category == "PII_REQUEST":

        print(
            "I cannot provide unauthorized "
            "personal information."
        )

        metrics.rejected += 1

        continue


    # -------------------------
    # Fail-Safe
    # -------------------------

    if category != "SAFE":

        print(
            "Request could not be safely processed."
        )

        metrics.rejected += 1

        continue


    # =====================================================
    # INTENT CLASSIFICATION
    # =====================================================

    intent = intent_agent.classify(
        query
    )

    print(
        f"[Intent Detected] {intent}"
    )


    # =====================================================
    # ROUTING
    # =====================================================

    route = routing_agent.route(
        intent
    )


    # =====================================================
    # REFUND STATUS WORKFLOW
    # =====================================================

    if route == "refund_status":

        order_id = input(
            "Enter Order ID: "
        ).strip()

        result = get_refund_status(
            order_id
        )

        print(result)

        continue


    # =====================================================
    # HUMAN ESCALATION WORKFLOW
    # =====================================================

    if route == "human":

        print(
            "Escalating to human support..."
        )

        metrics.escalated += 1

        continue


    # =====================================================
    # UNSUPPORTED INTENT
    # =====================================================

    if route != "refund":

        print(
            "Unsupported request"
        )

        continue


    # =====================================================
    # REFUND WORKFLOW
    # =====================================================

    order_id = input(
        "Enter Order ID: "
    ).strip()


    # -------------------------
    # Get Order
    # -------------------------

    order = get_order_details(
        order_id
    )


    if not order:

        metrics.rejected += 1

        print(
            "Order not found"
        )

        continue


    # =====================================================
    # POLICY VALIDATION
    # =====================================================

    eligible, reason = policy_agent.check(
        order
    )


    if not eligible:

        metrics.rejected += 1

        print(
            f"Refund rejected: {reason}"
        )

        continue


    # =====================================================
    # RISK ASSESSMENT
    # =====================================================

    risk = risk_agent.assess(
        order
    )


    if risk:

        metrics.escalated += 1

        print(
            "\nHigh-risk refund detected."
        )


        # -------------------------
        # HUMAN IN THE LOOP
        # -------------------------

        approved = human_review.review(
            order
        )


        if not approved:

            metrics.rejected += 1

            print(
                "Rejected by human reviewer"
            )

            continue


    # =====================================================
    # EXECUTE REFUND
    # =====================================================

    result = execution_agent.execute(
        order
    )


    # =====================================================
    # OUTPUT GUARDRAIL
    # =====================================================

    if not validate_output(
        result
    ):

        print(
            "Output validation failed"
        )

        metrics.rejected += 1

        continue


    # =====================================================
    # APPROVED
    # =====================================================

    metrics.approved += 1


    # =====================================================
    # AUDIT / EVALUATION
    # =====================================================

    evaluation_agent.log(
        result
    )


    print(
        result
    )


# =========================================================
# FINAL METRICS
# =========================================================

metrics.report()