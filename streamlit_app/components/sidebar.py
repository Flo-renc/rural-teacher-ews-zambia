import streamlit as st


NAV_ITEMS = [
    ("Overview",         "Overview"),
    ("At-Risk Schools",  "At-Risk Schools"),
    ("Teacher Trends",   "Teacher Trends"),
    ("Model Insights",   "Model Insights"),
    ("School Risk Map",  "School Risk Map"),
]


def render_sidebar():
    with st.sidebar:
        # Logo / branding block
        st.markdown("""
        <div style="padding: 1.75rem 1.25rem 1.25rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 0.75rem;">
            <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase;
                        color: #81C784; margin-bottom:0.35rem;">
                Ministry of Education · Zambia
            </div>
            <div style="font-size:1.15rem; font-weight:700; color:#fff; line-height:1.25; margin-bottom:0.5rem;">
                Teacher Attrition<br>Early Warning System
            </div>
            <div style="font-size:0.72rem; color:#A5D6A7; font-weight:400;">
                Academic Year 2024 / 2025
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown("""
        <div style="padding: 0.5rem 0; font-size:0.65rem; font-weight:700; letter-spacing:0.1em;
                    text-transform:uppercase; color:#81C784; padding-left:1.25rem; margin-bottom:0.25rem;">
            Navigation
        </div>
        """, unsafe_allow_html=True)

        labels = [item[0] for item in NAV_ITEMS]
        page   = st.radio(
            label="nav",
            options=labels,
            label_visibility="collapsed",
        )

        # Data status
        st.markdown("""
        <div style="position:absolute; bottom:0; left:0; right:0;
                    padding:1rem 1.25rem; border-top:1px solid rgba(255,255,255,0.1);">
            <div style="font-size:0.65rem; font-weight:600; letter-spacing:0.08em;
                        text-transform:uppercase; color:#81C784; margin-bottom:0.5rem;">
                Data Status
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
                <span style="width:7px;height:7px;border-radius:50%;background:#4CAF50;display:inline-block;"></span>
                <span style="font-size:0.76rem;color:#C8E6C9;">Bulletin 2022 — loaded</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
                <span style="width:7px;height:7px;border-radius:50%;background:#FFA726;display:inline-block;"></span>
                <span style="font-size:0.76rem;color:#C8E6C9;">EMIS data — pending</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span style="width:7px;height:7px;border-radius:50%;background:#4CAF50;display:inline-block;"></span>
                <span style="font-size:0.76rem;color:#C8E6C9;">Model v1.0 — active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return page