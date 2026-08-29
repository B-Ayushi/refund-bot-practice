import re
from typing import Any

PII_PATTERNS = [
    re.compile(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b"),
    re.compile(r"\b\d{6}\b"),
    re.compile(r"\b[A-Z]{5}\d{4}[A-Z]{1}\b"),
]

SENSITIVE_KEYWORDS = {
    "salary",
    "bank account",
    "address",
    "tax",
    "performance review",
    "salary credit",
    "payslip",
}


class SecurityPolicyError(ValueError):
    """Raised when a request violates security or policy rules."""


def detect_prompt_injection(message: str) -> bool:
    lower = message.lower()
    trigger_phrases = [
        "ignore all policies",
        "pretend you are hr admin",
        "bypass policy",
        "override approval",
        "disregard rules",
    ]
    return any(phrase in lower for phrase in trigger_phrases)


def detect_jailbreak_attempt(message: str) -> bool:
    lower = message.lower()
    jailbreak_patterns = [
        "system prompt",
        "developer mode",
        "act as admin",
        "ignore restrictions",
        "forget all your",
        "ignore all your",
        "disregard all",
        "pretend you don't",
        "pretend you are not",
        "you are not",
        "ignore guardrails",
        "bypass all",
    ]
    return any(p in lower for p in jailbreak_patterns)


def detect_pii(message: str) -> bool:
    return any(pattern.search(message) for pattern in PII_PATTERNS)


def validate_employee_access(employee_id: str, target_employee_id: str | None) -> bool:
    if target_employee_id is None:
        return True
    return employee_id == target_employee_id


def validate_request(message: str, employee_id: str, target_employee_id: str | None = None) -> None:
    if detect_prompt_injection(message):
        raise SecurityPolicyError("Prompt injection detected.")
    if detect_jailbreak_attempt(message):
        raise SecurityPolicyError("Jailbreak attempt detected.")
    if not validate_employee_access(employee_id, target_employee_id):
        raise SecurityPolicyError("Unauthorized access attempt.")
    if detect_pii(message):
        raise SecurityPolicyError("PII is not allowed in this request.")
    if any(keyword in message.lower() for keyword in SENSITIVE_KEYWORDS):
        raise SecurityPolicyError("Sensitive employee data request blocked.")
