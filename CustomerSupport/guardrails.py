BLOCKED = [
    "ignore instructions",
    "reveal system prompt",
    "show internal data"
]

def validate_input(query):

    q = query.lower()

    for phrase in BLOCKED:

        if phrase in q:
            return False

    return True