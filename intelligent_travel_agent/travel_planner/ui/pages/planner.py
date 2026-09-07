import asyncio
import streamlit as st
from travel_planner.llm.provider import GeminiUnavailableError
from travel_planner.ui.components.itinerary_view import render_itinerary
from travel_planner.ui.components.request_form import render_extraction_preview, render_request_form
from travel_planner.ui.components.review_view import render_review
from travel_planner.ui.components.weather_view import render_weather
from travel_planner.ui.components.workflow_visualizer import render_planning_agents, render_validation_agents, render_workflow
from travel_planner.ui.utils.formatters import to_jsonable
from travel_planner.ui.utils.session_state import add_history, planner


def _clarification_form(fields: list[str]) -> None:
    st.markdown("### A few details are needed")
    st.caption("The workflow pauses here until the TravelRequest contract is complete.")
    with st.form("clarification-form"):
        answers: dict[str, str] = {}
        if "destination" in fields:
            answers["destination"] = st.text_input("Where would you like to go?", placeholder="Enter a destination")
        if "duration" in fields:
            duration = st.number_input("How many days?", min_value=1, value=None, step=1, placeholder="Enter number of days")
            answers["duration"] = str(duration) if duration is not None else ""
        if "budget" in fields:
            budget = st.number_input("What is your maximum budget?", min_value=0, value=None, step=1000, placeholder="Enter maximum budget")
            answers["budget"] = str(budget) if budget is not None else ""
        if st.form_submit_button("Complete travel request", type="primary"):
            st.session_state.clarification_answers = answers
            st.session_state.clarification_ready = True
            st.rerun()


def _run_planner(raw_request: str) -> None:
    answers = st.session_state.get("clarification_answers", {})
    decision = st.session_state.get("weather_decision")
    alternative = st.session_state.get("alternative_destination")

    async def clarify(fields: list[str]) -> dict[str, str]:
        return {field: answers[field] for field in fields if field in answers}

    async def weather_decision(_validation: object) -> tuple[str, str | None]:
        if decision == "continue":
            return "continue", None
        if decision == "choose" and alternative:
            return "choose", alternative
        return "cancel", None

    with st.status("Running agent workflow", expanded=True) as status:
        st.write("Travel Request Understanding")
        st.session_state.workflow_events.append({"stage": "travel_request_understanding", "status": "passed"})
        st.write("Input Guardrails")
        st.session_state.workflow_events.append({"stage": "input_guardrails", "status": "passed"})
        st.write("Validation Loop fan-out")
        st.session_state.workflow_events.append({"stage": "validation_loop", "status": "running"})
        try:
            result = asyncio.run(planner().run(raw_request, clarify, weather_decision, st.session_state.session_id))
        except GeminiUnavailableError as error:
            st.session_state.gemini_error = str(error)
            st.session_state.result = None
            st.session_state.run_requested = False
            status.update(label="Gemini temporarily unavailable", state="error")
            st.error(str(error))
            return
        st.write("Planning and review complete" if result.planning else result.status)
        st.session_state.workflow_events.append({"stage": "planning_and_review", "status": result.status})
        status.update(label=f"Workflow {result.status.replace('_', ' ')}", state="complete")
    st.session_state.result = result
    st.session_state.run_requested = False
    st.session_state.weather_decision = None
    if result.planning:
        add_history(result)


def render_planner() -> None:
    request, submitted = render_request_form()
    if submitted:
        st.session_state.run_requested = True
        st.session_state.clarification_ready = False
        st.session_state.gemini_error = None
    if not request:
        render_workflow()
        st.info("Start with a destination and constraints, or describe the kind of break you need.")
        return
    if st.session_state.extracted_request is None or submitted:
        render_extraction_preview(request)
    if st.session_state.get("gemini_error"):
        return
    validation_preview = st.session_state.validation_preview
    if validation_preview and validation_preview.status != "complete" and not st.session_state.get("clarification_ready"):
        _clarification_form(validation_preview.missing_fields)
        return
    if st.session_state.get("run_requested"):
        _run_planner(request)
    result = st.session_state.get("result")
    render_workflow(result, st.session_state.extracted_request, validation_preview)
    if not result:
        return
    render_validation_agents(result)
    if result.validation and result.validation.status == "weather_warning" and not result.planning:
        render_weather(
            result,
            on_continue=lambda: (st.session_state.update(weather_decision="continue", run_requested=True), st.rerun()),
            on_choose=lambda destination: (st.session_state.update(weather_decision="choose", alternative_destination=destination, run_requested=True), st.rerun()),
        )
        return
    if result.planning:
        render_planning_agents(result)
        render_itinerary(result)
        render_review(result)
    elif result.message:
        st.error(result.message)
    if st.session_state.get("developer_mode"):
        with st.expander("Developer mode: full contracts"):
            st.json(to_jsonable(result))
            st.json({"workflow_events": st.session_state.get("workflow_events", [])})
