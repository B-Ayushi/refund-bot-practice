from datetime import datetime, timezone
from travel_planner.agents.base.agent import Agent
from travel_planner.schemas.travel_request import TravelRequest
from travel_planner.schemas.weather_result import WeatherResult
from travel_planner.tools.weather.client import WeatherClient
from travel_planner.providers.weather.open_meteo_provider import OpenMeteoProvider
from travel_planner.observability.logger import logger

class WeatherAgent(Agent[TravelRequest, WeatherResult]):
    name = "weather"
    def __init__(self, client: WeatherClient | None = None) -> None:
        self.client = client or WeatherClient(OpenMeteoProvider())

    async def run(self, request: TravelRequest) -> WeatherResult:
        if not request.destination or not request.destination.name:
            logger.event("weather_lookup_skipped", reason="destination_missing")
            return WeatherResult(
                request_id="", agent=self.name, created_at=datetime.now(timezone.utc), status="skipped",
                destination="", travel_window=(request.dates.start, request.dates.end),
                weather_summary="", source_timestamp=None, confidence=0.0,
            )
        if not request.is_complete():
            raise ValueError("WeatherAgent requires a complete TravelRequest")
        destination = request.destination_name
        logger.event("weather_lookup_started", destination=destination)
        try:
            data = await self.client.get_weather(destination, request.dates.start, request.dates.end)
        except Exception as error:
            logger.event(
                "weather_lookup_failed",
                provider_name=type(self.client.provider).__name__,
                provider_instance=type(self.client.provider).__name__,
                api_key_present=False,
                destination=destination,
                exception_type=type(error).__name__,
                exception=str(error),
            )
            return WeatherResult(
                request_id="", agent=self.name, created_at=datetime.now(timezone.utc), status="degraded",
                destination=destination, travel_window=(request.dates.start, request.dates.end),
                weather_summary="", source_timestamp=None, confidence=0.0,
            )
        logger.event("weather_lookup_success", destination=destination)
        status = "warning" if bool(data.get("warning")) else "pass"
        return WeatherResult(
            request_id="", agent=self.name, created_at=datetime.now(timezone.utc), status=status,
            destination=destination, travel_window=(request.dates.start, request.dates.end),
            weather_summary=str(data["summary"]), source_timestamp=str(data.get("retrieved_at")),
            confidence=0.9,
        )
