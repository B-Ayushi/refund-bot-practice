"""ADK refactorer agent."""

from google.adk.agents import LlmAgent

from ..instructions import load_instruction
from .observability import lifecycle_callbacks


class CodeRefactorerAgent(LlmAgent):
    """Improve generated code using the latest review."""

    def __init__(self, model: str = "gemini-3.6-flash") -> None:
        before_agent, after_agent = lifecycle_callbacks("Refactorer", "[refactorer]")
        super().__init__(
            name="code_refactorer",
            model=model,
            description="Refactors code to address every valid review finding.",
            instruction=load_instruction("refactorer.md"),
            output_key="generated_code",
            before_agent_callback=before_agent,
            after_agent_callback=after_agent,
        )