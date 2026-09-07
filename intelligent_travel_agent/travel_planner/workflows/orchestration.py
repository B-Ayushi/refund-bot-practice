from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from travel_planner.agents.extraction.clarification import Answers, ClarificationLoop
from travel_planner.agents.extraction.extractor import ExtractionLayer
from travel_planner.agents.extraction.validator import TravelRequestValidator
from travel_planner.llm.provider import StructuredExtractionProvider
from travel_planner.guardrails.input_guardrails import InputGuardrails
from travel_planner.memory.session_memory import SessionMemory
from travel_planner.schemas.itinerary_result import ItineraryDraft
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.workflows.planning_workflow import PlanningOutcome, PlanningWorkflow
from travel_planner.workflows.validation_workflow import ValidationOutcome, ValidationWorkflow
from travel_planner.tools.provider_errors import ProviderUnavailableError

@dataclass
class OrchestrationResult:
    status: str
    request: TravelRequest
    validation: ValidationOutcome | None = None
    planning: PlanningOutcome | None = None
    message: str | None = None

WeatherDecision = Callable[[ValidationOutcome], Awaitable[tuple[str, str | None]]]
Clarifier = Callable[[list[str]], Awaitable[Answers]]

class TravelPlanner:
    def __init__(self, memory: SessionMemory | None = None, extraction_provider: StructuredExtractionProvider | None = None) -> None:
        self.extractor = ExtractionLayer(extraction_provider)
        self.clarification = ClarificationLoop(TravelRequestValidator())
        self.guardrails = InputGuardrails()
        self.validation = ValidationWorkflow()
        self.planning = PlanningWorkflow()
        self.memory = memory or SessionMemory()

    async def run(self, raw_text: str, ask_clarification: Clarifier, ask_weather_decision: WeatherDecision, session_id: str = "default") -> OrchestrationResult:
        request = await self.extractor.extract(raw_text)
        request = self.memory.apply(session_id, request)
        request = await self.clarification.complete(request, ask_clarification)
        allowed, reason = await self.guardrails.check(raw_text)
        if not allowed:
            return OrchestrationResult("rejected", request, message=reason)
        for _ in range(3):
            validation = await self.validation.run(request)
            if validation.status == "weather_warning":
                action, destination = await ask_weather_decision(validation)
                if action == "continue":
                    validation.weather.status = "pass"
                    try:
                        planning = await self.planning.run(request, validation.weather)
                    except ProviderUnavailableError as error:
                        return OrchestrationResult("requires_provider", request, validation, message=str(error))
                    return OrchestrationResult("completed" if planning.review.status == "approve" else "needs_revision", request, validation, planning)
                if action == "choose" and destination:
                    if request.destination is None:
                        raise ValueError("cannot choose an alternative without a destination contract")
                    request.destination.name = destination
                    continue
                return OrchestrationResult("cancelled", request, validation, message="weather decision cancelled")
            if validation.status != "pass":
                return OrchestrationResult(validation.status, request, validation, message=validation.reason)
            try:
                planning = await self.planning.run(request, validation.weather)
            except ProviderUnavailableError as error:
                return OrchestrationResult("requires_provider", request, validation, message=str(error))
            return OrchestrationResult("completed" if planning.review.status == "approve" else "needs_revision", request, validation, planning)
        return OrchestrationResult("failed_terminal", request, message="validation iteration limit reached")
