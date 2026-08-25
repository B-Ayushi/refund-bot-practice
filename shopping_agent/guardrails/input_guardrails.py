BAD_PATTERNS = [

    "ignore instructions",
    "forget rules",
    "jailbreak"

]


def validate_input(
    query
):

    query = query.lower()

    for pattern in BAD_PATTERNS:

        if pattern in query:

            return False

    return True