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
    from views.login import render as render_login
    render_login()
    st.stop()

from components.sidebar import render_sidebar

page = render_sidebar()



# Navigate and execute the specific render function immediately
if page == "Overview":
    from views.overview import render
    render()

elif page == "At-Risk Provinces":
    from views.at_risk_provinces import render
    render()

elif page == "Province Trends":
    from views.province_trends import render
    render()

elif page == "Model Insights":
    from views.model_insights import render
    render()

elif page == "Province Risk Map":
    from views.province_risk_map import render
    render()
