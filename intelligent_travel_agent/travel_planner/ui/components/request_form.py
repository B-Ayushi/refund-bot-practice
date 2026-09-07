import streamlit as st
from travel_planner.llm.provider import GeminiUnavailableError
from travel_planner.ui.utils.session_state import planner
from travel_planner.ui.utils.formatters import to_jsonable


def render_request_form() -> tuple[str, bool]:
    st.markdown("## Plan a journey")
    st.caption("Describe the kind of trip you need. The planner will show how each agent evaluates it.")
    request = st.text_area(
        "Travel request",
        value=st.session_state.raw_request,
        height=112,
        placeholder="Plan a 5-day trip under ₹25,000",
        label_visibility="collapsed",
    )
    st.session_state.raw_request = request
    submitted = st.button("Run travel planner", type="primary", use_container_width=True)
    if submitted and request.strip():
        st.session_state.extracted_request = None
        st.session_state.validation_preview = None
        st.session_state.result = None
        st.session_state.weather_decision = None
        st.session_state.alternative_destination = ""
    return request.strip(), submitted and bool(request.strip())


def render_extraction_preview(request: str) -> None:
    extraction = planner().extractor
    validator = planner().clarification.validator
    import asyncio
    try:
        extracted = asyncio.run(extraction.extract(request))
    except GeminiUnavailableError as error:
        st.session_state.gemini_error = str(error)
        st.error(str(error))
        return
    st.session_state.extracted_request = extracted
    validation = validator.validate(extracted)
    st.session_state.validation_preview = validation
    left, right = st.columns(2)
    with left:
        st.markdown("### Travel Request Understanding")
        st.json(to_jsonable(extracted), expanded=False)
    with right:
        st.markdown("### Contract validation")
        if validation.status == "complete":
            st.success("Complete TravelRequest")
        else:
            st.warning("Clarification required")
            st.write("Missing: " + ", ".join(validation.missing_fields))
