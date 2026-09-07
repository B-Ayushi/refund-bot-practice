import streamlit as st


def render_review(result: object) -> None:
    review = result.planning.review
    if review.status == "approve":
        st.success("Reviewer approved the itinerary")
    else:
        st.warning("Reviewer requested revision")
        for finding in review.findings:
            st.write(f"• {finding}")
    checks = st.columns(3)
    checks[0].metric("Budget", review.budget_check.title())
    checks[1].metric("Completeness", review.completeness_check.title())
    checks[2].metric("Weather checked", "Yes" if review.weather_checked else "No")
