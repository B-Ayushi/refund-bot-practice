import streamlit as st
from travel_planner.ui.utils.formatters import money


def render_budget(itinerary: object) -> None:
    budget = itinerary.budget_breakdown
    st.markdown("### Budget breakdown")
    rows = {
        "Accommodation": budget.accommodation,
        "Food": budget.food,
        "Activities": budget.activities,
        "Local transport": budget.local_transport,
        "Contingency": budget.contingency,
    }
    st.table({"Category": list(rows), "Estimated cost": [money(value, budget.currency) for value in rows.values()]})
    st.metric("Estimated total", money(budget.total, budget.currency))
