from datetime import datetime, timezone
from typing import Any
import streamlit as st
from travel_planner.memory.preference_store import PreferenceStore
from travel_planner.memory.session_memory import SessionMemory
from travel_planner.workflows.orchestration import OrchestrationResult, TravelPlanner


def initialize_state() -> None:
    defaults: dict[str, Any] = {
        "session_id": "streamlit-session",
        "raw_request": "",
        "extracted_request": None,
        "validation_preview": None,
        "result": None,
        "history": [],
        "workflow_events": [],
        "developer_mode": False,
        "clarification_answers": {},
        "weather_decision": None,
        "alternative_destination": "",
        "gemini_error": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("memory_store", PreferenceStore())
    st.session_state.setdefault("planner", TravelPlanner(SessionMemory(st.session_state.memory_store)))


def planner() -> TravelPlanner:
    return st.session_state.planner


def add_history(result: OrchestrationResult) -> None:
    st.session_state.history.insert(0, {"result": result, "created_at": datetime.now(timezone.utc).isoformat()})
    st.session_state.history = st.session_state.history[:10]
