import asyncio
import json
from travel_planner.agents.validation.weather_agent import WeatherAgent
from travel_planner.schemas.travel_request import Budget, Days, Destination, TravelRequest
from travel_planner.providers.weather.open_meteo_provider import OpenMeteoProvider
from travel_planner.tools.weather.client import WeatherClient

def test_weather_requires_destination() -> None:
    async def scenario() -> None:
        request = TravelRequest(destination=Destination(name=None), days=Days(min=5, max=5), budget=Budget(max=25000))
        result = await WeatherAgent().run(request)
        assert result.status == "skipped"
        assert result.destination == ""

    asyncio.run(scenario())


def test_weather_agent_passes_with_open_meteo_data(monkeypatch) -> None:
    responses = [
        {"results": [{"latitude": 19.0, "longitude": 73.0}]},
        {"current": {"temperature_2m": 27.0, "precipitation_probability": 10, "weather_code": 0}},
    ]

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(responses.pop(0)).encode("utf-8")

    monkeypatch.setattr(
        "travel_planner.providers.weather.open_meteo_provider.urlopen",
        lambda *_args, **_kwargs: Response(),
    )
    request = TravelRequest(destination=Destination(name="Pune"), days=Days(min=5, max=5), budget=Budget(max=25000))
    result = asyncio.run(WeatherAgent(WeatherClient(OpenMeteoProvider())).run(request))
    assert result.status == "pass"
    assert result.destination == "Pune"
    assert "27.0" in result.weather_summary
