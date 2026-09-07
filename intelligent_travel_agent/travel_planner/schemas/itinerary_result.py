from pydantic import BaseModel, Field
from .common import AgentEnvelope

class ItineraryItem(BaseModel):
    start_time: str | None = None
    end_time: str | None = None
    type: str
    name: str
    location: str | None = None
    estimated_cost: float = Field(ge=0)
    currency: str = "INR"
    travel_time_minutes: int = Field(default=0, ge=0)
    optional: bool = False
    evidence_refs: list[str] = []

class ItineraryDay(BaseModel):
    day: int = Field(ge=1)
    date: str | None = None
    items: list[ItineraryItem] = []
    day_estimated_cost: float = Field(ge=0)

class BudgetBreakdown(BaseModel):
    accommodation: float = Field(ge=0)
    food: float = Field(ge=0)
    activities: float = Field(ge=0)
    local_transport: float = Field(ge=0)
    contingency: float = Field(ge=0)
    total: float = Field(ge=0)
    currency: str = "INR"

class ItineraryDraft(AgentEnvelope):
    schema_version: str = "itinerary_draft.v1"
    status: str = "draft"
    destination: str
    days: list[ItineraryDay]
    budget_breakdown: BudgetBreakdown
    assumptions: list[str] = []
    unresolved_items: list[str] = []
