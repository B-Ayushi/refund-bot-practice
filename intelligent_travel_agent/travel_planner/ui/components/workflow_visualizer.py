from typing import Any
import streamlit as st
from travel_planner.ui.utils.formatters import status_label, to_jsonable

_STATUS_ICONS = {"pending": "○", "running": "◐", "passed": "●", "warning": "!", "failed": "×"}


def _stage(status: str) -> None:
    normalized = "passed" if status in {"pass", "completed", "approve"} else status
    icon = _STATUS_ICONS.get(normalized, "○")
    st.markdown(f"<div class='stage stage-{normalized}'><span class='stage-icon'>{icon}</span><span>{status_label(normalized)}</span></div>", unsafe_allow_html=True)


def render_workflow(result: Any = None, extracted: Any = None, validation_preview: Any = None) -> None:
    st.markdown("## Orchestration flow")
    stages = ["pending"] * 5
    if extracted is not None:
        stages[0] = "passed" if validation_preview and validation_preview.status == "complete" else "warning"
    if result is not None:
        stages[0] = "passed"
        stages[1] = "failed" if result.status == "rejected" else "passed"
        if result.validation:
            stages[2] = "warning" if result.validation.status == "weather_warning" else ("failed" if result.validation.status.startswith("rejected") else "passed")
        if result.planning:
            stages[3] = "passed"
            stages[4] = "passed" if result.planning.review.status == "approve" else "warning"
    names = ["Travel Request Understanding", "Input Guardrails", "Validation Loop", "Planning Workflow", "Reviewer"]
    cols = st.columns(len(names))
    for column, name, status in zip(cols, names, stages):
        with column:
            st.caption(name)
            _stage(status)
    if result and st.session_state.get("developer_mode"):
        with st.expander("Workflow result contract"):
            st.json(to_jsonable(result))


def render_validation_agents(result: Any) -> None:
    st.markdown("### Validation fan-out")
    if not result or not result.validation:
        for name in ("Policy Agent", "Guardrail Agent", "Weather Agent"):
            with st.container(border=True):
                st.caption(name)
                _stage("pending")
        return
    validation = result.validation
    cards = [("Policy Agent", validation.policy.status, validation.policy), ("Guardrail Agent", validation.guardrail.status, validation.guardrail), ("Weather Agent", validation.weather.status, validation.weather)]
    cols = st.columns(3)
    for col, (name, status, payload) in zip(cols, cards):
        with col:
            with st.container(border=True):
                st.caption(name)
                _stage("warning" if status == "warning" else ("passed" if status == "pass" else "failed"))
                st.write(status_label(status))
                if name == "Weather Agent":
                    st.caption(payload.weather_summary)
                elif getattr(payload, "reason_code", None):
                    st.caption(payload.reason_code)
                if name == "Guardrail Agent":
                    st.caption(f"Intent: {payload.intent} · Confidence: {payload.confidence:.2f}")
                    st.caption(f"Decision: {'BLOCK' if payload.status == 'fail' else 'PASS'}")
                    st.caption(payload.reason)
                if st.session_state.get("developer_mode"):
                    st.json(to_jsonable(payload), expanded=False)


def render_planning_agents(result: Any) -> None:
    st.markdown("### Planning fan-out and synthesis")
    if not result or not result.planning:
        st.info("Hotel Agent and Attraction Agent will run in parallel after validation.")
        return
    planning = result.planning
    cols = st.columns(3)
    for col, name, status in zip(cols, ("Hotel Agent", "Attraction Agent", "Itinerary Agent"), ("passed", "passed", "passed")):
        with col:
            with st.container(border=True):
                st.caption(name)
                _stage(status)
    st.markdown("**Reviewer Agent**")
    _stage("passed" if planning.review.status == "approve" else "warning")
