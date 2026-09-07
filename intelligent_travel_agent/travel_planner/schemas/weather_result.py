from datetime import date
from typing import Literal
from .common import AgentEnvelope

class WeatherResult(AgentEnvelope):
    schema_version: str = "weather_result.v1"
    status: Literal["pass", "warning", "degraded", "skipped"]
    destination: str
    travel_window: tuple[date | None, date | None]
    weather_summary: str
    risk_factors: list[str] = []
    alternative_destinations: list[str] = []
    source_timestamp: str | None = None
    confidence: float = 0.0
