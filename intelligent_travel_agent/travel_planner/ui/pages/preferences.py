import streamlit as st
from travel_planner.memory.models import MemoryRecord
from travel_planner.ui.utils.session_state import planner


def render_preferences() -> None:
    st.markdown("## Preferences and memory")
    session_id = st.session_state.session_id
    records = planner().memory.store.get_all(session_id)
    if records:
        for key, record in records.items():
            left, right = st.columns([4, 1])
            left.write(f"**{key}**  ·  {record.value}")
            if right.button("Clear", key=f"clear-{key}"):
                planner().memory.store.delete(session_id, key)
                st.rerun()
    else:
        st.info("No saved preferences yet.")
    st.markdown("### Add a preference")
    key = st.selectbox("Preference", ["preferred_destinations", "preferred_hotel_type", "budget_preference", "previously_rejected_destinations"])
    value = st.text_input("Value")
    if st.button("Save preference") and value.strip():
        parsed: object = [item.strip() for item in value.split(",")] if "destinations" in key else value.strip()
        planner().memory.store.put(session_id, MemoryRecord(key=key, value=parsed))
        st.rerun()
