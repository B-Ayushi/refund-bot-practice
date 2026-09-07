from abc import ABC, abstractmethod

class GeminiUnavailableError(RuntimeError):
    """Raised after Gemini remains unavailable after the configured attempts."""

    def __init__(self, stage: str) -> None:
        super().__init__(f"Gemini is temporarily unavailable for {stage}. Please try again shortly.")
        self.stage = stage

class StructuredExtractionProvider(ABC):
    """Provider boundary for extracting structured travel requirements."""

    @abstractmethod
    async def extract_travel_request(self, user_text: str) -> str:
        """Return JSON text containing only extracted travel requirements."""
        raise NotImplementedError