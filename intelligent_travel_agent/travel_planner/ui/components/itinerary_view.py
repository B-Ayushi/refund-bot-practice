import streamlit as st
from travel_planner.ui.components.budget_view import render_budget
from travel_planner.ui.utils.formatters import money


def render_itinerary(result: object) -> None:
    itinerary = result.planning.itinerary
    request = result.request
    st.markdown("## Your travel plan")
    top = st.columns(3)
    top[0].metric("Destination", itinerary.destination)
    top[1].metric("Duration", f"{request.days.max} days")
    top[2].metric("Budget", money(request.budget.max, request.budget.currency))
    st.markdown("### Accommodation")
    first_day = itinerary.days[0] if itinerary.days else None
    accommodation = next((item for item in first_day.items if item.type == "check_in"), None) if first_day else None
    st.info(accommodation.name if accommodation else "Accommodation option included in the estimate")
    st.markdown("### Day-by-day itinerary")
    for day in itinerary.days:
        with st.container(border=True):
            st.markdown(f"**Day {day.day}**  ·  {money(day.day_estimated_cost, itinerary.budget_breakdown.currency)}")
            for item in day.items:
                st.write(f"{item.type.replace('_', ' ').title()}  ·  {item.name}  ·  {money(item.estimated_cost, item.currency)}")
    render_budget(itinerary)
