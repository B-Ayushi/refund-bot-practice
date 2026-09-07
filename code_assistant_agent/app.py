"""Streamlit UI for the existing autonomous code improvement workflow."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from autonomous_code_agent import root_agent

APP_NAME = "autonomous_code_agent"
USER_ID = "streamlit_user"


def _event_text(event: Any) -> str:
    """Return text from an ADK event, if it contains text content."""
    if not event.content or not event.content.parts:
        return ""
    return "\n".join(part.text for part in event.content.parts if part.text)


def _render_progress(lines: list[str], placeholder: Any) -> None:
    """Render the current workflow timeline."""
    placeholder.markdown("\n\n".join(f"- {line}" for line in lines))


def _append_stage(lines: list[str], stage: str, started: str, working: str) -> None:
    """Add a stage's live status to the timeline once."""
    if not any(stage in line for line in lines):
        lines.extend([started, working])


async def _run_workflow(requirement: str, progress: Any) -> tuple[str, str, str, str, str]:
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state={},
    )
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    message = types.Content(role="user", parts=[types.Part(text=requirement)])
    lines: list[str] = []
    writer_output = ""
    reviewer_feedback = ""
    refactorer_output = ""
    _append_stage(lines, "Writer", "[writer] Started", "[writer] Working")
    _render_progress(lines, progress)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=message,
    ):
        event_text = _event_text(event)
        author = event.author

        if author == "code_writer":
            if event_text and "completed" not in event_text.lower():
                writer_output = event_text
            lines = [line for line in lines if "Writer" not in line]
            lines.append("[writer] Completed")
            _append_stage(lines, "Reviewer", "[reviewer] Started", "[reviewer] Reviewing")
        elif author == "code_reviewer":
            if event_text and not event_text.startswith("[reviewer]"):
                reviewer_feedback = event_text
            try:
                review = json.loads(event_text)
                lines.append(f"[reviewer] Quality score: {review['quality_score']}")
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
            lines.append("[reviewer] Completed")
        elif author == "quality_gate":
            lines.append(event_text)
            if "threshold reached" in event_text:
                lines.append("[quality_gate] Approved")
            else:
                lines.append("[quality_gate] Needs improvement")
                _append_stage(
                    lines,
                    "Refactorer",
                    "[refactorer] Started",
                    "[refactorer] Refactoring",
                )
        elif author == "code_refactorer":
            if event_text and "complete" not in event_text.lower():
                refactorer_output = event_text
            lines = [line for line in lines if "Refactorer" not in line]
            lines.append("[refactorer] Refactoring complete")

        _render_progress(lines, progress)

    final_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session.id,
    )
    return (
        str(final_session.state.get("generated_code", "No generated code returned.")),
        "\n\n".join(f"- {line}" for line in lines),
        writer_output,
        reviewer_feedback,
        refactorer_output,
    )


st.set_page_config(page_title="Autonomous Code Assistant", page_icon=">", layout="wide")
st.title("Autonomous Code Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(message["progress"])
            with st.expander("Writer Output"):
                st.code(message.get("writer_output", "No writer output captured."), language="python")
            with st.expander("Reviewer Feedback"):
                st.code(message.get("reviewer_feedback", "No reviewer feedback captured."))
            with st.expander("Refactorer Output"):
                st.code(
                    message.get("refactorer_output", "Refactorer was not required."),
                    language="python",
                )
            with st.expander("Final generated code", expanded=True):
                st.code(message["code"], language="python")
        else:
            st.markdown(message["content"])

requirement = st.chat_input("Describe the software you want to generate")
if requirement:
    st.session_state.messages.append({"role": "user", "content": requirement})
    with st.chat_message("user"):
        st.markdown(requirement)
    with st.chat_message("assistant"):
        progress = st.empty()
        with st.status("Running workflow", expanded=True):
            (
                generated_code,
                progress_text,
                writer_output,
                reviewer_feedback,
                refactorer_output,
            ) = asyncio.run(_run_workflow(requirement, progress))
        st.markdown(progress_text)
        with st.expander("Writer Output"):
            st.code(writer_output or "No writer output captured.", language="python")
        with st.expander("Reviewer Feedback"):
            st.code(reviewer_feedback or "No reviewer feedback captured.")
        with st.expander("Refactorer Output"):
            st.code(refactorer_output or "Refactorer was not required.", language="python")
        with st.expander("Final generated code", expanded=True):
            st.code(generated_code, language="python")
    st.session_state.messages.append(
        {
            "role": "assistant",
            "progress": progress_text,
            "code": generated_code,
            "writer_output": writer_output,
            "reviewer_feedback": reviewer_feedback,
            "refactorer_output": refactorer_output,
        }
    )