from pydantic import BaseModel
from typing import Optional


class ExtractionBudget(BaseModel):
    currency: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    tier: Optional[str] = None


class ExtractionResponse(BaseModel):
    destination: Optional[str] = None
    days: Optional[int] = None
    budget: Optional[ExtractionBudget] = None
    extraction_confidence: Optional[float] = None