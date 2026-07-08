import streamlit as st


st.set_page_config(
    page_title="School Risk Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

from styles import inject_styles
inject_styles()

import api_client as api

if not st.session_state.get("access_token"):
    from views.login import render
    render()
    st.stop()

# Creat navigation only after login is successful

overview_page = st.Page("views/overview.py", title="Overview")
at_risk_schools_page = st.Page("views/at_risk_schools.py", title="At-Risk Schools")
teacher_trends_page = st.Page("views/teacher_trends.py", title="Teacher Trends")
model_insights_page = st.Page("views/model_insights.py", title="Model Insights")
school_risk_map_page = st.Page("views/school_risk_map.py", title="School Risk Map")

pg = st.navigation([
    overview_page,
    at_risk_schools_page,
    teacher_trends_page,
    model_insights_page,
    school_risk_map_page
]) 

pg.run()