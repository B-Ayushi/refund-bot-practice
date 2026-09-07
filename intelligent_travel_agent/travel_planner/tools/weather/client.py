from datetime import date
import os
from pathlib import Path
from dotenv import load_dotenv
from travel_planner.tools.weather.provider import WeatherProvider
from travel_planner.providers.weather.open_meteo_provider import OpenMeteoProvider
from travel_planner.observability.logger import logger

_ENV_PATH = Path(__file__).parents[2] / ".env"

class WeatherClient:
    def __init__(self, provider: WeatherProvider | None = None) -> None:
        load_dotenv(dotenv_path=_ENV_PATH)
        self.provider = provider or OpenMeteoProvider()
        logger.event(
            "weather_provider_registered",
            provider_name=os.getenv("WEATHER_PROVIDER", "open_meteo"),
            provider_instance=type(self.provider).__name__,
            api_key_present=False,
        )

    async def get_weather(self, destination: str, start: date | None, end: date | None) -> dict[str, object]:
        logger.event(
            "weather_provider_lookup",
            provider_name=os.getenv("WEATHER_PROVIDER", "open_meteo"),
            provider_instance=type(self.provider).__name__,
            api_key_present=False,
            destination=destination,
        )
        return await self.provider.get_weather(destination, start, end)
