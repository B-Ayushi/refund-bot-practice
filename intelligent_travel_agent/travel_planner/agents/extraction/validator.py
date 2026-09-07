from pydantic import BaseModel
from travel_planner.schemas.travel_request import TravelRequest

class ValidationResult(BaseModel):
    status: str
    missing_fields: list[str] = []

class TravelRequestValidator:
    def validate(self, request: TravelRequest) -> ValidationResult:
        missing = request.missing_required_fields()
        return ValidationResult(status="complete" if not missing else "needs_clarification", missing_fields=missing)
