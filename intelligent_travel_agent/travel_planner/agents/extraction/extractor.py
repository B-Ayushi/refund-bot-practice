from travel_planner.llm.gemini_provider import GeminiProvider
from travel_planner.llm.parsers.travel_request_parser import TravelRequestParser
from travel_planner.llm.provider import StructuredExtractionProvider
from travel_planner.llm.provider import GeminiUnavailableError
from travel_planner.observability.logger import logger
from travel_planner.schemas.travel_request import TravelRequest

class ExtractionLayer:
    """Extracts a TravelRequest through a provider and validates it before return."""
    def __init__(self, provider: StructuredExtractionProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()
        self.parser = TravelRequestParser()

    async def extract(self, text: str) -> TravelRequest:
        logger.event("extraction_started")
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                raw_response = await self.provider.extract_travel_request(text)
                request = self.parser.parse(raw_response)
                logger.event("extraction_completed", confidence=request.extraction_confidence)
                logger.event("extraction_success", confidence=request.extraction_confidence)
                return request
            except Exception as error:
                last_error = error
                logger.event("extraction_validation_failed", attempt=attempt + 1, error=str(error))
                if attempt == 0:
                    logger.event("extraction_retry")
        raise GeminiUnavailableError("travel request extraction") from last_error
