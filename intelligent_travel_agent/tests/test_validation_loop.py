import asyncio
from travel_planner.workflows.validation_workflow import ValidationWorkflow
from travel_planner.schemas.travel_request import Budget, Days, Destination, TravelRequest

class SlowAgent:
    async def run(self, request: TravelRequest) -> object:
        await asyncio.sleep(0.01)
        return None

def complete_request() -> TravelRequest:
    return TravelRequest(destination=Destination(name="Goa"), days=Days(min=5, max=5), budget=Budget(max=25000))

def test_validation_rejects_incomplete_request() -> None:
    async def scenario() -> None:
        request = complete_request()
        request.destination.name = None
        try:
            await ValidationWorkflow().run(request)
        except ValueError as error:
            assert "complete" in str(error)
        else:
            raise AssertionError("expected incomplete request to be rejected")

    asyncio.run(scenario())

def test_validation_fans_out_and_passes() -> None:
    async def scenario() -> None:
        outcome = await ValidationWorkflow().run(complete_request())
        assert outcome.status == "requires_provider"
        assert outcome.weather.status == "degraded"

    asyncio.run(scenario())
