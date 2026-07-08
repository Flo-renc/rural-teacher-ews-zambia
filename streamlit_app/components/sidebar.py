import streamlit as st
from api_client import api

NAV_ITEMS = [
    "Overview",
    "At-Risk Schools",
    "Teacher Trends",
    "Model Insights",
    "School Risk Map",
]


def render_sidebar():

    with st.sidebar:

        st.markdown("""
        <div style="
            padding:1.75rem 1.25rem 1.25rem;
            border-bottom:1px solid rgba(255,255,255,0.12);
            margin-bottom:0.75rem;
        ">
            <div style="
                font-size:0.65rem;
                font-weight:700;
                letter-spacing:0.12em;
                color:#81C784;
            ">
                MINISTRY OF EDUCATION · ZAMBIA
            </div>

            <div style="
                font-size:1.15rem;
                font-weight:700;
                color:white;
                line-height:1.25;
            ">
                Teacher Attrition<br>
                Early Warning System
            </div>

            <div style="
                font-size:0.72rem;
                color:#A5D6A7;
            ">
                Academic Year 2024 / 2025
            </div>
        </div>
        """, unsafe_allow_html=True)



        st.markdown(
            """
            <div style="
                padding-left:1.25rem;
                font-size:0.65rem;
                font-weight:700;
                color:#81C784;
                text-transform:uppercase;
            ">
            Navigation
            </div>
            """,
            unsafe_allow_html=True
        )


        page = st.radio(
            "Choose page",
            options=NAV_ITEMS,
            label_visibility="collapsed"
        )


        st.markdown("""
        <div style="
            margin-top:2rem;
            padding:1rem 1.25rem;
            border-top:1px solid rgba(255,255,255,0.1);
        ">

        <div style="
            font-size:0.65rem;
            font-weight:600;
            color:#81C784;
        ">
        DATA STATUS
        </div>

        <p>🟢 Bulletin 2022 — loaded</p>
        <p>🟠 EMIS data — pending</p>
        <p>🟢 Model v1.0 — active</p>

        </div>
        """,
        unsafe_allow_html=True)

        user = api.get_current_user()

        st.markdown("""
        <div style="
            margin-top:2rem;
            padding:1rem 1.25rem;
            border-top:1px solid rgba(255,255,255,0.1);
        ">
            <div style="
                font-size:0.65rem;
                font-weight:700;
                color:#81C784;
            ">
            LOGGED IN AS
            </div>
            </div>
        """, unsafe_allow_html=True
        )

        if user:
            st.markdown(
                f"""
                <div style="
                    padding-left: 1.25rem;
                    color: white;
                ">
                <b>{user.get("username", "User")}</b><br>
                <spam styles="color: #A5D6A7;">
                </span><br>
                <span style = "color: #A5D6A7;">
                {user.get("province", "")}
                </span>
                </div>
                """, unsafe_allow_html=True 
            )
        if st.button("Logout", use_container_width=True):
            api.logout()
            st.rerun()

    return page