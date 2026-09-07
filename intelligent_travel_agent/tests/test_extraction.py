import asyncio
from travel_planner.llm.parsers.travel_request_parser import TravelRequestParser
from travel_planner.agents.extraction.validator import TravelRequestValidator

def test_extraction_requires_clarification_for_missing_destination() -> None:
    async def scenario() -> None:
        request = TravelRequestParser().parse('{"destination":null,"days":7,"budget":{"tier":"budget"}}')
        result = TravelRequestValidator().validate(request)
        assert result.status == "needs_clarification"
        assert "destination" in result.missing_fields

    asyncio.run(scenario())
