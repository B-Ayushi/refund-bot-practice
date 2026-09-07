from abc import ABC, abstractmethod
from datetime import date

class WeatherProvider(ABC):
    @abstractmethod
    async def get_weather(self, destination: str, start: date | None, end: date | None) -> dict[str, object]:
        raise NotImplementedError