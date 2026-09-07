from datetime import datetime, timezone

from pydantic import BaseModel, Field

from travel_planner.agents.base.agent import Agent
from travel_planner.agents.planning.attraction_agent import AttractionSearchResult
from travel_planner.agents.planning.gemini_support import PlanningGemini
from travel_planner.agents.planning.hotel_agent import HotelSearchOutput
from travel_planner.schemas.itinerary_result import BudgetBreakdown, ItineraryDay, ItineraryDraft, ItineraryItem
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.schemas.weather_result import WeatherResult

class PlanningInput(BaseModel):
    request: TravelRequest
    hotels: HotelSearchOutput
    attractions: AttractionSearchResult
    weather: WeatherResult


class GeneratedActivity(BaseModel):
    name: str
    type: str
    location: str | None = None
    estimated_cost: float = Field(ge=0)
    currency: str
    optional: bool = False


class GeneratedDay(BaseModel):
    day: int = Field(ge=1)
    activities: list[GeneratedActivity]


class GeneratedBudget(BaseModel):
    accommodation: float = Field(ge=0)
    food: float = Field(ge=0)
    activities: float = Field(ge=0)
    local_transport: float = Field(ge=0)
    contingency: float = Field(ge=0)
    total: float = Field(ge=0)
    currency: str


class ItineraryResponse(BaseModel):
    days: list[GeneratedDay]
    budget_breakdown: GeneratedBudget

class ItineraryAgent(Agent[PlanningInput, ItineraryDraft]):
    name = "itinerary"

    def __init__(self, gemini: PlanningGemini | None = None) -> None:
        self.gemini = gemini or PlanningGemini()

    async def run(self, input_data: PlanningInput) -> ItineraryDraft:
        request = input_data.request
        if not request.is_complete() or not request.days or not request.destination or not request.budget:
            raise ValueError("ItineraryAgent requires a complete TravelRequest")
        response = await self.gemini.generate(
            self.name,
            "itinerary_planning.md",
            {
                "destination": request.destination_name,
                "duration_days": request.days.max,
                "budget": request.budget.model_dump(mode="json"),
                "weather": input_data.weather.model_dump(mode="json"),
                "hotels": input_data.hotels.model_dump(mode="json"),
                "attractions": input_data.attractions.model_dump(mode="json"),
            },
            ItineraryResponse,
        )
        days = [
            ItineraryDay(
                day=day.day,
                items=[
                    ItineraryItem(
                        type=activity.type,
                        name=activity.name,
                        location=activity.location,
                        estimated_cost=activity.estimated_cost,
                        currency=activity.currency,
                        optional=activity.optional,
                    )
                    for activity in day.activities
                ],
                day_estimated_cost=sum(activity.estimated_cost for activity in day.activities),
            )
            for day in response.days
        ]
        unresolved = [] if len(days) == request.days.max else ["Generated itinerary day count does not match requested duration"]
        return ItineraryDraft(
            request_id="",
            agent=self.name,
            created_at=datetime.now(timezone.utc),
            destination=request.destination_name,
            days=days,
            budget_breakdown=BudgetBreakdown(**response.budget_breakdown.model_dump()),
            unresolved_items=unresolved,
        )
