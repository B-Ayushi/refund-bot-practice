import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel
from google.genai import types

from travel_planner.llm.gemini_provider import GeminiProvider
from travel_planner.llm.provider import GeminiUnavailableError
from travel_planner.observability.logger import logger

ModelT = TypeVar("ModelT", bound=BaseModel)
_MODEL = "gemini-3.6-flash"
_PROMPT_DIR = Path(__file__).parents[2] / "llm" / "prompts"


class PlanningGemini:
    """Shared planning adapter that reuses the extraction provider's Gemini client."""

    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

    async def generate(self, agent: str, prompt_name: str, payload: dict[str, Any], schema: type[ModelT]) -> ModelT:
        prompt = (_PROMPT_DIR / prompt_name).read_text(encoding="utf-8")
        contents = f"{prompt}\n\nINPUT JSON:\n{json.dumps(payload, default=str)}"
        last_error: Exception | None = None
        for attempt in range(2):
            logger.event("planning_extraction_started", agent=agent, attempt=attempt + 1)
            try:
                response = await self.provider.client.aio.models.generate_content(
                    model=_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=0.1,
                    ),
                )
                if not response.text:
                    raise ValueError("Gemini returned an empty planning response")
                parsed = schema.model_validate_json(response.text)
                logger.event("planning_extraction_success", agent=agent, attempt=attempt + 1)
                return parsed
            except Exception as error:
                last_error = error
                logger.event("planning_extraction_failed", agent=agent, attempt=attempt + 1, error=str(error))
                if attempt == 0:
                    logger.event("planning_extraction_retry", agent=agent)
        raise GeminiUnavailableError(f"{agent} planning") from last_error