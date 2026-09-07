import asyncio
from dataclasses import dataclass
from travel_planner.agents.planning.attraction_agent import AttractionAgent
from travel_planner.agents.planning.gemini_support import PlanningGemini
from travel_planner.agents.planning.hotel_agent import HotelAgent
from travel_planner.schemas.attraction_result import AttractionSearchResult
from travel_planner.schemas.itinerary_result import ItineraryDraft
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.agents.planning.itinerary_agent import ItineraryAgent, PlanningInput
from travel_planner.agents.reviewer.reviewer_agent import ReviewerAgent, ReviewInput
from travel_planner.schemas.review_result import ReviewResult
from travel_planner.observability.logger import logger

@dataclass
class PlanningOutcome:
    itinerary: ItineraryDraft
    review: ReviewResult

class PlanningWorkflow:
    def __init__(self) -> None:
        gemini = PlanningGemini()
        self.hotel = HotelAgent(gemini)
        self.attraction = AttractionAgent(gemini)
        self.itinerary = ItineraryAgent(gemini)
        self.reviewer = ReviewerAgent(gemini)

    async def run(self, request: TravelRequest, weather: object) -> PlanningOutcome:
        if not request.is_complete():
            raise ValueError("PlanningWorkflow requires a complete TravelRequest")
        logger.event("workflow_transition", stage="planning_fan_out", status="started")
        hotels, attractions = await asyncio.gather(self.hotel.run(request), self.attraction.run(request))
        draft = await self.itinerary.run(PlanningInput(request=request, hotels=hotels, attractions=attractions, weather=weather))
        review = await self.reviewer.run(
            ReviewInput(
                request=request,
                itinerary=draft,
                weather=weather,
                hotels=hotels,
                attractions=attractions,
            )
        )
        logger.event("workflow_transition", stage="review", status=review.status)
        return PlanningOutcome(draft, review)
