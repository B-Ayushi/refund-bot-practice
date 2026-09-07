import asyncio
from travel_planner.agents.planning.reviewer_agent import ReviewerAgent, ReviewInput
from travel_planner.schemas.itinerary_result import BudgetBreakdown, ItineraryDay, ItineraryDraft
from travel_planner.schemas.travel_request import Budget, Days, Destination, TravelRequest
from travel_planner.schemas.weather_result import WeatherResult
from datetime import datetime, timezone

def test_reviewer_rejects_plan_without_provider_evidence() -> None:
    async def scenario() -> None:
        request = TravelRequest(destination=Destination(name="Goa"), days=Days(min=5, max=5), budget=Budget(max=25000))
        itinerary = ItineraryDraft(
            request_id="", agent="itinerary", created_at=datetime.now(timezone.utc), destination="Goa",
            days=[ItineraryDay(day=1, items=[], day_estimated_cost=0)],
            budget_breakdown=BudgetBreakdown(accommodation=0, food=0, activities=0, local_transport=0, contingency=0, total=0),
        )
        weather = WeatherResult(
            request_id="", agent="weather", created_at=datetime.now(timezone.utc), status="pass",
            destination="Goa", travel_window=(None, None), weather_summary="verified", confidence=1.0,
        )
        review = await ReviewerAgent().run(ReviewInput(request=request, itinerary=itinerary, weather=weather))
        assert review.status == "request_revision"

    asyncio.run(scenario())
