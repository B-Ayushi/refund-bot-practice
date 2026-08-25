from datetime import datetime, timezone


def request_handoff(
    memory,
    query
):

    handoff = {
        "status": "human_handoff_requested",
        "query": query,
        "requested_at": datetime.now(timezone.utc).isoformat()
    }

    memory.update(
        "handoff",
        handoff
    )

    return (
        "Human handoff requested. Your shopping conversation has been "
        "prepared for a human specialist."
    )
