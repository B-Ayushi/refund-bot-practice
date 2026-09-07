import asyncio

from travel_planner.agents.extraction.clarification import ClarificationLoop
from travel_planner.agents.extraction.validator import TravelRequestValidator
from travel_planner.llm.parsers.travel_request_parser import TravelRequestParser
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.workflows.planning_workflow import PlanningWorkflow
from travel_planner.workflows.validation_workflow import ValidationWorkflow

def parse(payload: str):
    return TravelRequestParser().parse(payload)


def test_missing_destination_blocks_workflow() -> None:
    async def scenario() -> None:
        request = parse('{"destination":null,"days":5,"budget":{"max":25000}}')
        assert request.missing_required_fields() == ["destination"]
        try:
            await ValidationWorkflow().run(request)
        except ValueError as error:
            assert "complete" in str(error)
        else:
            raise AssertionError("validation accepted a missing destination")

    asyncio.run(scenario())


def test_explicit_destination_duration_and_budget_are_extracted() -> None:
    async def scenario() -> None:
        request = parse('{"destination":"Goa","days":5,"budget":{"max":25000}}')
        assert request.is_complete()
        assert request.destination is not None and request.destination.name == "Goa"
        assert request.days is not None and request.days.max == 5
        assert request.budget is not None and request.budget.max == 25000

    asyncio.run(scenario())


def test_missing_budget_blocks_workflow() -> None:
    async def scenario() -> None:
        request = parse('{"destination":"Goa","days":5,"budget":null}')
        assert request.missing_required_fields() == ["budget"]
        try:
            await PlanningWorkflow().run(request, object())
        except ValueError as error:
            assert "complete" in str(error)
        else:
            raise AssertionError("planning accepted a missing budget")

    asyncio.run(scenario())


def test_missing_duration_blocks_workflow() -> None:
    async def scenario() -> None:
        request = parse('{"destination":"Goa","days":null,"budget":{"max":25000}}')
        assert request.missing_required_fields() == ["duration"]
        try:
            await ValidationWorkflow().run(request)
        except ValueError as error:
            assert "complete" in str(error)
        else:
            raise AssertionError("validation accepted a missing duration")

    asyncio.run(scenario())


def test_all_missing_fields_trigger_clarification() -> None:
    async def scenario() -> None:
        request = parse('{"destination":null,"days":null,"budget":null}')
        assert request.destination is None
        assert request.days is None
        assert request.budget is None
        validation = TravelRequestValidator().validate(request)
        assert validation.missing_fields == ["destination", "duration", "budget"]
        asked: list[str] = []

        async def ask(fields: list[str]) -> dict[str, str]:
            asked.extend(fields)
            return {"destination": "Goa", "duration": "5", "budget": "25000"}

        completed = await ClarificationLoop().complete(request, ask)
        assert asked == ["destination", "duration", "budget"]
        assert completed.is_complete()

    asyncio.run(scenario())


def test_planning_cannot_execute_with_incomplete_contract() -> None:
    async def scenario() -> None:
        request = parse('{"destination":null,"days":null,"budget":null}')
        try:
            await PlanningWorkflow().run(request, object())
        except ValueError as error:
            assert "complete" in str(error)
        else:
            raise AssertionError("planning accepted an incomplete contract")

    asyncio.run(scenario())


def test_validation_cannot_execute_with_incomplete_contract() -> None:
    async def scenario() -> None:
        request = TravelRequest()
        try:
            await ValidationWorkflow().run(request)
        except ValueError as error:
            assert "complete" in str(error)
        else:
            raise AssertionError("validation accepted an incomplete contract")

    asyncio.run(scenario())
