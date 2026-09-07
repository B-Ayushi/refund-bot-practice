import re

BLOCKED_PATTERNS = (r"ignore previous instructions", r"reveal system prompt", r"jailbreak")

def detect_malicious(text: str) -> list[str]:
    return [pattern for pattern in BLOCKED_PATTERNS if re.search(pattern, text, re.I)]
