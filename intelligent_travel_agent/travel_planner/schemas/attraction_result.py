from datetime import datetime
from .common import AgentEnvelope

class AttractionOption(AgentEnvelope):
    schema_version: str = "attraction_option.v1"
    name: str
    category: str
    estimated_duration_hours: float
    estimated_cost: float
    currency: str = "INR"
    weather_sensitivity: str = "low"
    opening_constraints: list[str] = []

class AttractionSearchResult(AgentEnvelope):
    schema_version: str = "attraction_search_result.v1"
    status: str
    destination: str
    options: list[AttractionOption] = []
    limitations: list[str] = []
