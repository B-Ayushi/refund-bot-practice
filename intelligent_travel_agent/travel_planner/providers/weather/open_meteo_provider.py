import asyncio
import json
from datetime import date, datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from travel_planner.tools.weather.provider import WeatherProvider
from travel_planner.observability.logger import logger

_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

_WEATHER_CODES = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


class OpenMeteoProvider(WeatherProvider):
    async def get_weather(
        self,
        destination: str,
        start: date | None = None,
        end: date | None = None,
    ) -> dict[str, object]:
        geocoding_request = self._build_geocoding_request(destination)
        logger.event(
            "weather_api_request_started",
            provider_name="open_meteo",
            provider_instance=type(self).__name__,
            api_key_present=False,
            destination=destination,
            request_url=geocoding_request.full_url,
        )
        geocoding = await asyncio.to_thread(self._get_json, geocoding_request, destination)
        results = geocoding.get("results")
        if not isinstance(results, list) or not results:
            raise ValueError(f"Open-Meteo could not geocode destination: {destination}")
        location = results[0]
        if not isinstance(location, dict) or "latitude" not in location or "longitude" not in location:
            raise ValueError("Open-Meteo geocoding response omitted coordinates")

        forecast_request = self._build_forecast_request(float(location["latitude"]), float(location["longitude"]))
        logger.event(
            "weather_api_request_started",
            provider_name="open_meteo",
            provider_instance=type(self).__name__,
            api_key_present=False,
            destination=destination,
            request_url=forecast_request.full_url,
        )
        forecast = await asyncio.to_thread(self._get_json, forecast_request, destination)
        current = forecast.get("current")
        if not isinstance(current, dict):
            raise ValueError("Open-Meteo forecast response omitted current weather")
        temperature = current.get("temperature_2m")
        rain_probability = current.get("precipitation_probability")
        weather_code = current.get("weather_code")
        if not isinstance(temperature, (int, float)) or not isinstance(rain_probability, (int, float)):
            raise ValueError("Open-Meteo forecast response omitted required weather values")
        conditions = _WEATHER_CODES.get(int(weather_code), "unknown conditions")
        return {
            "temperature": float(temperature),
            "rain_probability": int(rain_probability),
            "conditions": conditions,
            "summary": f"{conditions}; {float(temperature):.1f}°C; {int(rain_probability)}% precipitation probability",
            "warning": int(rain_probability) >= 60 or int(weather_code) in {65, 82, 95, 96, 99},
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "source": "open-meteo",
            "destination": destination,
            "start": start,
            "end": end,
        }

    @staticmethod
    def _build_geocoding_request(destination: str) -> Request:
        query = urlencode({"name": destination, "count": 1, "language": "en", "format": "json"})
        return Request(f"{_GEOCODING_URL}?{query}", headers={"Accept": "application/json"})

    @staticmethod
    def _build_forecast_request(latitude: float, longitude: float) -> Request:
        query = urlencode({
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,precipitation_probability,weather_code",
            "timezone": "auto",
        })
        return Request(f"{_FORECAST_URL}?{query}", headers={"Accept": "application/json"})

    @staticmethod
    def _get_json(request: Request, destination: str) -> dict[str, object]:
        try:
            with urlopen(request, timeout=10) as response:
                logger.event(
                    "weather_api_response",
                    provider_name="open_meteo",
                    provider_instance="OpenMeteoProvider",
                    api_key_present=False,
                    destination=destination,
                    request_url=request.full_url,
                    response_status=getattr(response, "status", None),
                )
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            logger.event(
                "weather_api_exception",
                provider_name="open_meteo",
                provider_instance="OpenMeteoProvider",
                api_key_present=False,
                destination=destination,
                request_url=request.full_url,
                exception_type=type(error).__name__,
                exception=str(error),
            )
            raise RuntimeError(f"Open-Meteo request failed: {error}") from error
        if not isinstance(payload, dict):
            raise ValueError("Open-Meteo returned a non-object response")
        return payload