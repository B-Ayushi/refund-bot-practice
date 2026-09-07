import streamlit as st
from travel_planner.ui.utils.formatters import to_jsonable


def render_weather(result: object, on_continue: object, on_choose: object) -> None:
    weather = result.validation.weather
    st.markdown("### Weather risk")
    st.warning(weather.weather_summary)
    if weather.risk_factors:
        st.write(" · ".join(weather.risk_factors))
    st.caption(f"Checked at {weather.source_timestamp or 'provider response time'}")
    if weather.alternative_destinations:
        st.markdown("#### Alternative destinations")
        choice = st.selectbox("Choose an alternative", weather.alternative_destinations, key="alternative_destination")
    else:
        choice = ""
    left, right = st.columns(2)
    with left:
        if st.button("Continue anyway", type="primary", use_container_width=True):
            on_continue()
    with right:
        if st.button("Choose alternative destination", use_container_width=True, disabled=not bool(choice)):
            on_choose(choice)
    if st.session_state.get("developer_mode"):
        with st.expander("Weather contract"):
            st.json(to_jsonable(weather))
