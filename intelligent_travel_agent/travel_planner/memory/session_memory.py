from .preference_store import PreferenceStore
from travel_planner.schemas.travel_request import TravelRequest

class SessionMemory:
    def __init__(self, store: PreferenceStore | None = None) -> None:
        self.store = store or PreferenceStore()

    def context(self, session_id: str) -> dict[str, object]:
        return {key: record.value for key, record in self.store.get_all(session_id).items()}

    def apply(self, session_id: str, request: TravelRequest) -> TravelRequest:
        context = self.context(session_id)
        if "preferred_hotel_type" in context:
            request.preferences.setdefault("hotel_category", context["preferred_hotel_type"])
        if request.budget is not None and "budget_preference" in context and request.budget.tier is None:
            request.budget.tier = str(context["budget_preference"])
        avoided = context.get("previously_rejected_destinations", [])
        if isinstance(avoided, list):
            request.constraints.extend(f"avoid:{destination}" for destination in avoided if f"avoid:{destination}" not in request.constraints)
        return request
