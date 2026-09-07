"""Lifecycle callbacks shared by the workflow's LLM agents."""

import logging
from collections.abc import Callable

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

logger = logging.getLogger(__name__)


def lifecycle_callbacks(
    agent_label: str, icon: str, *, counts_iterations: bool = False
) -> tuple[Callable, Callable]:
    """Return ADK callbacks that log lifecycle state and emit completion progress."""

    def before_agent(callback_context: CallbackContext) -> None:
        if counts_iterations:
            callback_context.state["iteration"] = int(
                callback_context.state.get("iteration", 0)
            ) + 1
        logger.info(
            "%s %s started",
            icon,
            agent_label,
            extra={"agent": agent_label, "status": "started"},
        )
        logger.info(
            "%s %s running",
            icon,
            agent_label,
            extra={"agent": agent_label, "status": "running"},
        )

    def after_agent(callback_context: CallbackContext) -> types.Content:
        logger.info(
            "%s %s completed",
            icon,
            agent_label,
            extra={"agent": agent_label, "status": "completed"},
        )
        return types.Content(
            role="model",
            parts=[types.Part(text=f"{icon} {agent_label} completed")],
        )

    return before_agent, after_agent