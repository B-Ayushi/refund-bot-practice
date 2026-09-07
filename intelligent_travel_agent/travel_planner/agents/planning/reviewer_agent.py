from datetime import datetime, timezone
from travel_planner.agents.base.agent import Agent
from pydantic import BaseModel
from travel_planner.schemas.itinerary_result import ItineraryDraft
from travel_planner.schemas.review_result import ReviewResult
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.schemas.weather_result import WeatherResult

class ReviewInput(BaseModel):
    request: TravelRequest
    itinerary: ItineraryDraft
    weather: WeatherResult

class ReviewerAgent(Agent[ReviewInput, ReviewResult]):
    name = "reviewer"
    async def run(self, input_data: ReviewInput) -> ReviewResult:
        request, itinerary, weather = input_data.request, input_data.itinerary, input_data.weather
        findings: list[str] = []
        if len(itinerary.days) != request.days.max:
            findings.append("itinerary does not contain the requested number of days")
        if weather.status not in ("pass", "warning"):
            findings.append("weather was not successfully checked")
        if request.budget.max is not None and itinerary.budget_breakdown.total > request.budget.max:
            findings.append("estimated budget exceeds maximum")
        if itinerary.unresolved_items:
            findings.extend(itinerary.unresolved_items)
        if any(not item.evidence_refs for day in itinerary.days for item in day.items):
            findings.append("itinerary items are missing provider evidence")
        status = "approve" if not findings else "request_revision"
        return ReviewResult(request_id="", agent=self.name, created_at=datetime.now(timezone.utc), status=status, findings=findings, budget_check="pass" if "estimated budget exceeds maximum" not in findings else "fail", completeness_check="pass" if len(itinerary.days) == request.days.max else "fail", weather_checked=weather.status in ("pass", "warning"), revision_instructions=findings)
