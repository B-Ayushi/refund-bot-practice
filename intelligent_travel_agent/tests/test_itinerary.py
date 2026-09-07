import asyncio
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.workflows.planning_workflow import PlanningWorkflow

def test_planning_rejects_incomplete_request_before_gemini() -> None:
    async def scenario() -> None:
        request = TravelRequest()
        try:
            await PlanningWorkflow().run(request, object())
        except ValueError as error:
            assert "complete" in str(error)
        else:
            raise AssertionError("planning accepted an incomplete TravelRequest")

    asyncio.run(scenario())
