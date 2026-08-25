BLOCKED_PATTERNS = [

    "ignore all instructions",

    "forget your instructions",

    "override policy",

    "bypass policy",

    "reveal system prompt",

    "show internal prompt"
]


def validate_input(query):

    query = query.lower()

    for pattern in BLOCKED_PATTERNS:

        if pattern in query:

            return False

    return True