PROHIBITED_TERMS = ("illegal", "weapon", "explosive")

def violates_policy(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in PROHIBITED_TERMS)
