from datetime import datetime, timezone

from pydantic import BaseModel

from travel_planner.agents.base.agent import Agent
from travel_planner.agents.planning.attraction_agent import AttractionSearchResult
from travel_planner.agents.planning.gemini_support import PlanningGemini
from travel_planner.agents.planning.hotel_agent import HotelSearchOutput
from travel_planner.schemas.itinerary_result import ItineraryDraft
from travel_planner.schemas.review_result import ReviewResult
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.schemas.weather_result import WeatherResult


class ReviewInput(BaseModel):
    request: TravelRequest
    itinerary: ItineraryDraft
    weather: WeatherResult
    hotels: HotelSearchOutput
    attractions: AttractionSearchResult


class ReviewerResponse(BaseModel):
    status: str
    issues: list[str]
    summary: str


class ReviewerAgent(Agent[ReviewInput, ReviewResult]):
    name = "reviewer"

    def __init__(self, gemini: PlanningGemini | None = None) -> None:
        self.gemini = gemini or PlanningGemini()

    async def run(self, input_data: ReviewInput) -> ReviewResult:
        response = await self.gemini.generate(
            self.name,
            "review_planning.md",
            {
                "travel_request": input_data.request.model_dump(mode="json"),
                "itinerary": input_data.itinerary.model_dump(mode="json"),
                "weather": input_data.weather.model_dump(mode="json"),
                "hotels": input_data.hotels.model_dump(mode="json"),
                "attractions": input_data.attractions.model_dump(mode="json"),
            },
            ReviewerResponse,
        )
        status = "approve" if response.status.upper() == "PASS" else "request_revision"
        issues = list(response.issues)
        return ReviewResult(
            request_id="",
            agent=self.name,
            created_at=datetime.now(timezone.utc),
            status=status,
            findings=issues or [response.summary] if status == "request_revision" else [],
            budget_check="fail" if any("budget" in issue.lower() for issue in issues) else "pass",
            completeness_check="fail" if any("day" in issue.lower() or "duration" in issue.lower() for issue in issues) else "pass",
            weather_checked=input_data.weather.status in {"pass", "warning"},
            revision_instructions=issues,
        )