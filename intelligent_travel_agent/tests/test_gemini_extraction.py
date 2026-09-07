import asyncio

from travel_planner.agents.extraction.clarification import ClarificationLoop
from travel_planner.agents.extraction.extractor import ExtractionLayer
from travel_planner.llm.parsers.travel_request_parser import TravelRequestParser
from travel_planner.llm.provider import StructuredExtractionProvider

class RecordedProvider(StructuredExtractionProvider):
    def __init__(self, response: str | None = None, responses: list[str] | None = None) -> None:
        self.response = response
        self.responses = responses or []
        self.calls = 0

    async def extract_travel_request(self, user_text: str) -> str:
        self.calls += 1
        if self.responses:
            return self.responses.pop(0)
        return self.response or '{"destination":null,"days":null,"budget":null}'


def run(coro: object) -> object:
    return asyncio.run(coro)  # type: ignore[arg-type]


def test_destination_extraction() -> None:
    request = run(ExtractionLayer(RecordedProvider(response='{"destination":"Goa","days":5,"budget":{"max":25000}}')).extract("Goa"))
    assert request.destination is not None and request.destination.name == "Goa"


def test_budget_extraction() -> None:
    request = run(ExtractionLayer(RecordedProvider(response='{"destination":null,"days":null,"budget":{"currency":"INR","max":25000}}')).extract("budget"))
    assert request.budget is not None and request.budget.max == 25000


def test_duration_extraction() -> None:
    request = run(ExtractionLayer(RecordedProvider(response='{"destination":null,"days":7,"budget":null}')).extract("week"))
    assert request.days is not None and request.days.max == 7


def test_missing_destination() -> None:
    request = run(ExtractionLayer(RecordedProvider(response='{"destination":null,"days":5,"budget":{"max":25000}}')).extract("trip"))
    assert request.missing_required_fields() == ["destination"]


def test_missing_duration() -> None:
    request = run(ExtractionLayer(RecordedProvider(response='{"destination":"Goa","days":null,"budget":{"max":25000}}')).extract("trip"))
    assert request.missing_required_fields() == ["duration"]


def test_missing_budget() -> None:
    request = run(ExtractionLayer(RecordedProvider(response='{"destination":"Goa","days":5,"budget":null}')).extract("trip"))
    assert request.missing_required_fields() == ["budget"]


def test_mixed_natural_language_structured_response() -> None:
    response = '{"destination":null,"days":7,"budget":{"tier":"budget"},"extraction_confidence":0.9}'
    request = run(ExtractionLayer(RecordedProvider(response=response)).extract("I am tired from work and want a budget-friendly vacation for a week."))
    assert request.destination is None
    assert request.days is not None and request.days.max == 7
    assert request.budget is not None and request.budget.tier == "budget"


def test_malformed_model_output() -> None:
    try:
        TravelRequestParser().parse("not json")
    except ValueError as error:
        assert "valid JSON" in str(error)
    else:
        raise AssertionError("malformed output was accepted")


def test_validation_retry() -> None:
    provider = RecordedProvider(responses=["not json", '{"destination":"Goa","days":5,"budget":{"max":25000}}'])
    request = run(ExtractionLayer(provider).extract("trip"))
    assert provider.calls == 2
    assert request.is_complete()


def test_clarification_fallback_after_missing_model_fields() -> None:
    request = run(ExtractionLayer(RecordedProvider(response='{"destination":null,"days":null,"budget":null}')).extract("Plan a trip"))

    async def ask(fields: list[str]) -> dict[str, str]:
        assert fields == ["destination", "duration", "budget"]
        return {"destination": "Goa", "duration": "5", "budget": "25000"}

    completed = run(ClarificationLoop().complete(request, ask))
    assert completed.is_complete()