"""Google ADK orchestration for the writer-reviewer-refactorer loop."""

import json
import logging
from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types

from ..agents.refactorer import CodeRefactorerAgent
from ..agents.reviewer import CodeReviewerAgent
from ..agents.writer import CodeWriterAgent

logger = logging.getLogger(__name__)


class QualityGateAgent(BaseAgent):
    """Stop the ADK loop when the reviewer reports production-ready quality."""

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        review = ctx.session.state.get("review_result", {})
        if isinstance(review, str):
            review = json.loads(review)
        if isinstance(review, dict):
            score = int(review.get("quality_score", 0))
        else:
            score = 0
        ctx.session.state["quality_score"] = score
        iteration = ctx.session.state.get("iteration", 0)
        should_stop = score >= 95
        reason = "quality threshold reached" if should_stop else "quality threshold not reached"
        logger.info(
            "Iteration %s: quality score=%s; %s",
            iteration,
            score,
            reason,
            extra={
                "iteration": iteration,
                "quality_score": score,
                "decision": "stop" if should_stop else "continue",
            },
        )
        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=(
                            f"[Iteration {iteration}] Quality score = {score}; "
                            f"{reason}."
                        )
                    )
                ],
            ),
            actions=EventActions(escalate=should_stop),
        )


class CodeImprovementWorkflow(BaseAgent):
    """Run code generation and iterative improvement through Google ADK."""

    def __init__(self, model: str = "gemini-3.6-flash", max_iterations: int = 10) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        writer = CodeWriterAgent(model=model)
        reviewer = CodeReviewerAgent(model=model)
        refactorer = CodeRefactorerAgent(model=model)
        loop = LoopAgent(
            name="code_quality_loop",
            max_iterations=max_iterations,
            sub_agents=[reviewer, QualityGateAgent(name="quality_gate"), refactorer],
        )
        super().__init__(
            name="autonomous_code_improvement",
            description="Generates, reviews, and refactors code until quality reaches 95.",
            sub_agents=[SequentialAgent(name="generation_and_quality", sub_agents=[writer, loop])],
        )

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        ctx.session.state["requirement"] = "\n".join(
            part.text for part in ctx.user_content.parts if part.text
        )
        async for event in self.sub_agents[0].run_async(ctx):
            yield event