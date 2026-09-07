from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from travel_planner.llm.provider import StructuredExtractionProvider
from travel_planner.llm.parsers.extraction_response import ExtractionResponse

_PROMPT_PATH = Path(__file__).parent / "prompts" / "extraction.md"
_ENV_PATH = Path(__file__).parents[1] / ".env"

_MODEL = "gemini-3.6-flash"


class GeminiProvider(StructuredExtractionProvider):
    """Gemini-only adapter for structured travel extraction."""

    def __init__(self, api_key: str | None = None) -> None:
        load_dotenv(dotenv_path=_ENV_PATH)

        key = api_key or os.getenv("GEMINI_API_KEY")

        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is required for Gemini extraction"
            )

        self.client = genai.Client(api_key=key)
        self.prompt = _PROMPT_PATH.read_text(encoding="utf-8")

    async def extract_travel_request(self, user_text: str) -> str:
        response = await self.client.aio.models.generate_content(
            model=_MODEL,
            contents=f"{self.prompt}\n\nUSER REQUEST:\n{user_text}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResponse,
                temperature=0.1,
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty extraction response"
            )

        return response.text