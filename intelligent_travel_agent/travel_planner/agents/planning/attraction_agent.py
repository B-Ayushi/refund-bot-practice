from datetime import datetime, timezone

from pydantic import BaseModel, Field

from travel_planner.agents.base.agent import Agent
from travel_planner.agents.planning.gemini_support import PlanningGemini
from travel_planner.schemas.common import AgentEnvelope
from travel_planner.schemas.travel_request import TravelRequest


class AttractionRecommendation(BaseModel):
    name: str
    type: str
    reason: str


class AttractionSearchResult(AgentEnvelope):
    schema_version: str = "attraction_search_result.v1"
    status: str
    destination: str
    options: list[AttractionRecommendation]


class AttractionResponse(BaseModel):
    attractions: list[AttractionRecommendation] = Field(min_length=5, max_length=10)

class AttractionAgent(Agent[TravelRequest, AttractionSearchResult]):
    name = "attraction"
    def __init__(self, gemini: PlanningGemini | None = None) -> None:
        self.gemini = gemini or PlanningGemini()

    async def run(self, request: TravelRequest) -> AttractionSearchResult:
        if not request.is_complete() or not request.destination or not request.days:
            raise ValueError("AttractionAgent requires a complete destination and duration")
        response = await self.gemini.generate(
            self.name,
            "attraction_planning.md",
            {
                "destination": request.destination_name,
                "duration_days": request.days.max,
                "preferences": request.preferences,
                "interests": request.interests,
                "trip_type": request.trip_type,
            },
            AttractionResponse,
        )
        return AttractionSearchResult(
            request_id="",
            agent=self.name,
            created_at=datetime.now(timezone.utc),
            status="success",
            destination=request.destination_name,
            options=response.attractions,
        )
