from datetime import date
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class DateRange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: date | None = None
    end: date | None = None

    @model_validator(mode="after")
    def validate_order(self) -> "DateRange":
        if self.start and self.end and self.start > self.end:
            raise ValueError("start must be before end")
        return self

class Days(BaseModel):
    model_config = ConfigDict(extra="forbid")
    min: int = Field(ge=1)
    max: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_range(self) -> "Days":
        if self.min > self.max:
            raise ValueError("days.min must not exceed days.max")
        return self

class Party(BaseModel):
    model_config = ConfigDict(extra="forbid")
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)

class Budget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    currency: str = "INR"
    min: float | None = Field(default=None, ge=0)
    max: float | None = Field(default=None, ge=0)
    tier: Literal["budget", "midrange", "luxury"] | None = None
    includes: list[str] = Field(default_factory=lambda: ["accommodation", "food", "activities", "local_transport"])

    @model_validator(mode="after")
    def validate_range(self) -> "Budget":
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("budget.min must not exceed budget.max")
        return self

class Destination(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    country: str | None = None
    confidence: float = Field(default=0.0, ge=0, le=1)
    user_provided: bool = False

class TravelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = "travel_request.v1"
    destination: Destination | None = None
    origin: str | None = None
    dates: DateRange = Field(default_factory=DateRange)
    days: Days | None = None
    party: Party = Field(default_factory=Party)
    budget: Budget | None = None
    trip_type: str | None = None
    interests: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    clarifications_required: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    extraction_confidence: float = Field(default=0.0, ge=0, le=1)

    @property
    def destination_name(self) -> str:
        if not self.destination or not self.destination.name:
            raise ValueError("destination is required")
        return self.destination.name

    def missing_required_fields(self) -> list[str]:
        missing: list[str] = []
        if not self.destination or not self.destination.name:
            missing.append("destination")
        if self.days is None:
            missing.append("duration")
        if self.budget is None:
            missing.append("budget")
        return missing

    def is_complete(self) -> bool:
        return not self.missing_required_fields()
