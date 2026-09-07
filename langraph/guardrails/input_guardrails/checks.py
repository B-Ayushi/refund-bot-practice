import re


JAILBREAK_PATTERNS = (
    r"\b(ignore|forget|disregard|bypass|override)\b.{0,40}\b(instructions|rules|prompt|policy)\b",
    r"\b(pretend|act)\b.{0,30}\b(developer|system|admin|unrestricted)\b",
    r"\b(dan|do anything now)\b",
)

PROMPT_INJECTION_PATTERNS = (
    r"\b(reveal|show|print|repeat|tell me)\b.{0,50}\b(system prompt|developer message|hidden instructions|internal instructions)\b",
    r"\b(api key|secret key|password|credential|environment variable|\.env)\b",
    r"\b(chain of thought|hidden reasoning|private reasoning)\b",
)

ABUSIVE_PATTERNS = (
    r"\b(stupid|idiot|moron|shut up|hate you)\b",
    r"\b(kill yourself|hurt you|threat)\b",
)

OUT_OF_SCOPE_PATTERNS = (
    r"\b(weather|recipe|homework|politics|stock price|write code|joke)\b",
)


def _matches(query, patterns):
    return any(re.search(pattern, query, re.IGNORECASE) for pattern in patterns)


def input_guardrail(state):
    query = state["user_query"]

    if _matches(query, JAILBREAK_PATTERNS):
        return {"input_allowed": False, "guardrail_reason": "jailbreak"}
    if _matches(query, PROMPT_INJECTION_PATTERNS):
        return {"input_allowed": False, "guardrail_reason": "prompt injection"}
    if _matches(query, ABUSIVE_PATTERNS):
        return {"input_allowed": False, "guardrail_reason": "abusive content"}
    if _matches(query, OUT_OF_SCOPE_PATTERNS):
        return {"input_allowed": False, "guardrail_reason": "out of scope"}

    return {"input_allowed": True, "guardrail_reason": ""}


def route_input(state):
    return "allowed" if state.get("input_allowed") else "blocked"


def intent_guardrail(state):
    allowed_intents = {"refund", "cancel", "status", "faq"}
    if not state.get("input_allowed") or state.get("intent") not in allowed_intents:
        return {"intent": "blocked", "guardrail_reason": state.get("guardrail_reason", "invalid intent")}

    return {}
