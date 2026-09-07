import re


SENSITIVE_OUTPUT_PATTERNS = (
    r"system prompt",
    r"developer message",
    r"hidden instructions",
    r"api key",
    r"secret key",
    r"password",
    r"credential",
    r"environment variable",
    r"chain of thought",
)

UNSUPPORTED_CLAIM_PATTERNS = (
    r"\b(refund|cancellation) approved\b",
    r"\b(order|refund|cancellation) completed\b",
)

SAFE_REFUSAL = (
    "I can only help with order status, cancellations, refunds, "
    "and related order questions."
)


def output_guardrail(state):
    result = state.get("result", "")
    if any(re.search(pattern, result, re.IGNORECASE) for pattern in SENSITIVE_OUTPUT_PATTERNS):
        return {"result": SAFE_REFUSAL, "output_allowed": False}
    if any(re.search(pattern, result, re.IGNORECASE) for pattern in UNSUPPORTED_CLAIM_PATTERNS):
        return {"result": SAFE_REFUSAL, "output_allowed": False}

    return {"result": result, "output_allowed": True}
