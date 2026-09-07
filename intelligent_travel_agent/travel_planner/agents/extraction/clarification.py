from collections.abc import Awaitable, Callable
from travel_planner.config.constants import MAX_CLARIFICATION_ATTEMPTS
from travel_planner.schemas.travel_request import Budget, Days, Destination, TravelRequest
from .validator import TravelRequestValidator

Answers = dict[str, str]

class ClarificationLoop:
    def __init__(self, validator: TravelRequestValidator | None = None) -> None:
        self.validator = validator or TravelRequestValidator()

    async def complete(self, request: TravelRequest, ask: Callable[[list[str]], Awaitable[Answers]]) -> TravelRequest:
        for _ in range(MAX_CLARIFICATION_ATTEMPTS):
            result = self.validator.validate(request)
            if result.status == "complete":
                return request
            answers = await ask(result.missing_fields)
            answers = {key: value for key, value in answers.items() if str(value).strip()}
            if not answers:
                raise ValueError("user abandoned request")
            if "destination" in answers:
                request.destination = Destination(name=answers["destination"], user_provided=True, confidence=1.0)
            if "budget" in answers:
                request.budget = Budget(max=float(answers["budget"]))
            if "duration" in answers:
                duration = int(answers["duration"])
                request.days = Days(min=duration, max=duration)
        raise ValueError("maximum clarification attempts reached")
