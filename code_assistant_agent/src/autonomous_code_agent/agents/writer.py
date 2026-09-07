"""ADK writer agent."""

from google.adk.agents import LlmAgent

from ..instructions import load_instruction
from .observability import lifecycle_callbacks


class CodeWriterAgent(LlmAgent):
    """Generate a complete implementation for a natural-language requirement."""

    def __init__(self, model: str = "gemini-3.6-flash") -> None:
        before_agent, after_agent = lifecycle_callbacks("Writer", "[writer]")
        super().__init__(
            name="code_writer",
            model=model,
            description="Generates an initial production-ready implementation.",
            instruction=load_instruction("writer.md"),
            output_key="generated_code",
            before_agent_callback=before_agent,
            after_agent_callback=after_agent,
        )