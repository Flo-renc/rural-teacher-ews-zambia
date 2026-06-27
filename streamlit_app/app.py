import streamlit as st

st.set_page_config(
    page_title="Teacher Attrition EWS | Zambia MoE",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles import inject_styles
inject_styles()

from components.sidebar import render_sidebar
page = render_sidebar()

if page == "Overview":
    from pages.overview import render
elif page == "At-Risk Schools":
    from pages.at_risk_schools import render
elif page == "Teacher Trends":
    from pages.teacher_trends import render
elif page == "Model Insights":
    from pages.model_insights import render
elif page == "School Risk Map":
    from pages.school_risk_map import render

render()