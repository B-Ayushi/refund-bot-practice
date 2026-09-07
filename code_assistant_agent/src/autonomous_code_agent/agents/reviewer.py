"""ADK reviewer agent."""

from google.adk.agents import LlmAgent

from ..instructions import load_instruction
from .observability import lifecycle_callbacks


class CodeReviewerAgent(LlmAgent):
    """Review generated code and return a quality score with actionable findings."""

    def __init__(self, model: str = "gemini-3.6-flash") -> None:
        before_agent, after_agent = lifecycle_callbacks(
            "Reviewer", "[reviewer]", counts_iterations=True
        )
        super().__init__(
            name="code_reviewer",
            model=model,
            description="Reviews implementation quality against the original requirement.",
            instruction=load_instruction("reviewer.md"),
            output_key="review_result",
            before_agent_callback=before_agent,
            after_agent_callback=after_agent,
        )