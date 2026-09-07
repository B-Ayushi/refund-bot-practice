import streamlit as st
from travel_planner.ui.utils.formatters import money, status_label


def render_history() -> None:
    st.markdown("## Plan history")
    history = st.session_state.get("history", [])
    if not history:
        st.info("Completed plans will appear here.")
        return
    for index, result in enumerate(history):
        record = result
        result = record["result"] if isinstance(record, dict) else record
        created_at = record.get("created_at", "") if isinstance(record, dict) else ""
        with st.container(border=True):
            columns = st.columns([2, 1, 1, 1])
            columns[0].markdown(f"**{result.request.destination.name or 'Destination pending'}**")
            columns[1].write(f"{result.request.days.max} days")
            columns[2].write(money(result.request.budget.max, result.request.budget.currency))
            columns[3].write(created_at[:10] if created_at else status_label(result.status))
            st.caption(f"Status: {status_label(result.status)}")
            if st.button("Reopen", key=f"history-{index}"):
                st.session_state.result = result
                st.session_state.page = "Planner"
                st.rerun()
