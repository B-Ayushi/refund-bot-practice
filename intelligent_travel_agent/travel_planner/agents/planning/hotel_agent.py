from datetime import datetime, timezone

from pydantic import BaseModel, Field

from travel_planner.agents.base.agent import Agent
from travel_planner.agents.planning.gemini_support import PlanningGemini
from travel_planner.schemas.common import AgentEnvelope
from travel_planner.schemas.travel_request import TravelRequest


class HotelRecommendation(BaseModel):
    name: str
    reason: str
    price_range: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)


class HotelSearchOutput(AgentEnvelope):
    schema_version: str = "hotel_search_result.v1"
    status: str
    destination: str
    options: list[HotelRecommendation]


class HotelResponse(BaseModel):
    hotels: list[HotelRecommendation] = Field(min_length=3, max_length=5)


class HotelAgent(Agent[TravelRequest, HotelSearchOutput]):
    name = "hotel"

    def __init__(self, gemini: PlanningGemini | None = None) -> None:
        self.gemini = gemini or PlanningGemini()

    async def run(self, request: TravelRequest) -> HotelSearchOutput:
        if not request.is_complete() or not request.destination or not request.budget or not request.days:
            raise ValueError("HotelAgent requires a complete TravelRequest")
        response = await self.gemini.generate(
            self.name,
            "hotel_planning.md",
            {
                "destination": request.destination_name,
                "duration_days": request.days.max,
                "budget": request.budget.model_dump(mode="json"),
            },
            HotelResponse,
        )
        return HotelSearchOutput(
            request_id="",
            agent=self.name,
            created_at=datetime.now(timezone.utc),
            status="success",
            destination=request.destination_name,
            options=response.hotels,
        )
