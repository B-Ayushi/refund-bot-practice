def classify_intent(query):

    query = query.lower()

    if "password" in query:
        return "faq"

    if "order" in query and "arrive" in query:
        return "tracking"

    if "cancel" in query:
        return "cancellation"

    if "human" in query:
        return "escalation"

    return "unknown"