from travel_planner.schemas.itinerary_result import ItineraryDraft

def validate_output(plan: ItineraryDraft) -> None:
    if not plan.days:
        raise ValueError("itinerary must contain days")
    if plan.budget_breakdown.total < 0:
        raise ValueError("budget total cannot be negative")
