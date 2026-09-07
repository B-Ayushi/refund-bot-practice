from travel_planner.tools.provider_errors import ProviderUnavailableError

class HotelClient:
    async def search(self, destination: str) -> list[dict[str, object]]:
        raise ProviderUnavailableError("hotel")
