import asyncio
import logging
import sys
from travel_planner.workflows.orchestration import TravelPlanner

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    planner = TravelPlanner()

    async def clarify(fields: list[str]) -> dict[str, str]:
        raise ValueError(f"Missing required travel fields: {', '.join(fields)}")

    async def weather_decision(_validation: object) -> tuple[str, str | None]:
        return "continue", None

    user_text = " ".join(sys.argv[1:]).strip()
    if not user_text:
        raise ValueError("Provide a travel request as command-line arguments")
    result = await planner.run(user_text, clarify, weather_decision)
    print(result.model_dump_json(indent=2) if hasattr(result, "model_dump_json") else result)

if __name__ == "__main__":
    asyncio.run(main())
