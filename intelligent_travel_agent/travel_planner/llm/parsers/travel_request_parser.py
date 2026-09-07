import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from travel_planner.schemas.travel_request import Budget, Days, Destination, TravelRequest

class ExtractedBudget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    currency: str | None = None
    min: float | None = Field(default=None, ge=0)
    max: float | None = Field(default=None, ge=0)
    tier: str | None = None

class ExtractedTravelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: str | None = None
    days: int | None = Field(default=None, ge=1)
    budget: ExtractedBudget | None = None
    extraction_confidence: float | None = Field(default=None, ge=0, le=1)

class TravelRequestParser:
    def parse(self, response_text: str) -> TravelRequest:
        payload = self._load_json(response_text)
        extracted = ExtractedTravelRequest.model_validate(payload)
        budget = None
        if extracted.budget is not None:
            budget = Budget(
                currency=extracted.budget.currency or "INR",
                min=extracted.budget.min,
                max=extracted.budget.max,
                tier=extracted.budget.tier if extracted.budget.tier in {"budget", "midrange", "luxury"} else None,
            )
        return TravelRequest(
            destination=Destination(name=extracted.destination, user_provided=True, confidence=1.0) if extracted.destination else None,
            days=Days(min=extracted.days, max=extracted.days) if extracted.days is not None else None,
            budget=budget,
            extraction_confidence=extracted.extraction_confidence or 0.0,
        )

    @staticmethod
    def _load_json(response_text: str) -> dict[str, Any]:
        text = response_text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            value = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError("Gemini response was not valid JSON") from error
        if not isinstance(value, dict):
            raise ValueError("Gemini response must be a JSON object")
        return value