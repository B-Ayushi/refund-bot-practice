import asyncio
import json

from travel_planner.providers.weather.open_meteo_provider import OpenMeteoProvider


def test_open_meteo_geocodes_and_normalizes_weather(monkeypatch) -> None:
    responses = [
        {"results": [{"latitude": 48.8566, "longitude": 2.3522}]},
        {
            "current": {
                "temperature_2m": 21.5,
                "precipitation_probability": 35,
                "weather_code": 2,
            }
        },
    ]

    class Response:
        def __init__(self, payload: dict[str, object]) -> None:
            self.payload = payload

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(self.payload).encode("utf-8")

    monkeypatch.setattr(
        "travel_planner.providers.weather.open_meteo_provider.urlopen",
        lambda *_args, **_kwargs: Response(responses.pop(0)),
    )
    result = asyncio.run(OpenMeteoProvider().get_weather("Paris"))
    assert result["temperature"] == 21.5
    assert result["rain_probability"] == 35
    assert result["conditions"] == "partly cloudy"
    assert result["source"] == "open-meteo"


def test_open_meteo_rejects_unknown_destination(monkeypatch) -> None:
    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"results": []}'

    monkeypatch.setattr(
        "travel_planner.providers.weather.open_meteo_provider.urlopen",
        lambda *_args, **_kwargs: Response(),
    )
    try:
        asyncio.run(OpenMeteoProvider().get_weather("unknown destination"))
    except ValueError as error:
        assert "could not geocode" in str(error)
    else:
        raise AssertionError("unknown destination was accepted")