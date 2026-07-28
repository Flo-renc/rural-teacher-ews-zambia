import streamlit as st
import api_client as api

NAV_ITEMS = [
    "Overview",
    "At-Risk Provinces",
    "Province Trends",
    "Model Insights",
    "Province Risk Map",
    "Privacy & Terms"
]

def get_navigation():

    nav_items = NAV_ITEMS.copy()

    user = api.get_current_user()

    if user and user.get("role") == "data_admin":
        nav_items.append("Administration")

    return nav_items

def render_sidebar():
    
    with st.sidebar:

        # ── Branding ──────────────────────────────────────────
        st.markdown("""
        <div style="
            padding: 1.75rem 1.25rem 1.25rem;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            margin-bottom: 0.75rem;
        ">
            <div style="
                font-size: 0.65rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                color: #81C784;
                margin-bottom: 0.35rem;
            ">
                MINISTRY OF EDUCATION · ZAMBIA
            </div>
            <div style="
                font-size: 1.15rem;
                font-weight: 700;
                color: white;
                line-height: 1.25;
                margin-bottom: 0.5rem;
            ">
                Teacher Attrition<br>Early Warning System
            </div>
            <div style="font-size: 0.72rem; color: #A5D6A7;">
                Academic Year 2024 / 2025
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation label ──────────────────────────────────
        st.markdown("""
        <div style="
            padding-left: 1.25rem;
            margin-bottom: 0.25rem;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #81C784;
        ">Navigation</div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Choose page",
            options=get_navigation(),
            label_visibility="collapsed",
        )

        # ── Data status ───────────────────────────────────────
        st.markdown("""
        <div style="
            margin-top: 2rem;
            padding: 1rem 1.25rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        ">
            <div style="
                font-size: 0.65rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: #81C784;
                margin-bottom: 0.6rem;
            ">Data Status</div>
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
                <span style="width:7px;height:7px;border-radius:50%;background:#4CAF50;
                             display:inline-block;flex-shrink:0;"></span>
                <span style="font-size:0.76rem; color:#C8E6C9;">Bulletin 2009-2025 — loaded</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
                <span style="width:7px;height:7px;border-radius:50%;background:#FFA726;
                             display:inline-block;flex-shrink:0;"></span>
                <span style="font-size:0.76rem; color:#C8E6C9;">EMIS school data — pending</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span style="width:7px;height:7px;border-radius:50%;background:#4CAF50;
                             display:inline-block;flex-shrink:0;"></span>
                <span style="font-size:0.76rem; color:#C8E6C9;">xgb_v1.0 — active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Logged-in user ────────────────────────────────────
        # Read directly from session state — more reliable than api.get_current_user()
        user = st.session_state.get("current_user")

        if user:
            username = user.get("username", "User")
            role     = user.get("role", "viewer").replace("_", " ").title()
            province = user.get("province") or ""

            st.markdown(f"""
            <div style="
                margin-top: 0.5rem;
                padding: 0.85rem 1.25rem;
                border-top: 1px solid rgba(255,255,255,0.1);
            ">
                <div style="
                    font-size: 0.65rem;
                    font-weight: 700;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                    color: #81C784;
                    margin-bottom: 0.4rem;
                ">Logged In As</div>
                <div style="font-size: 0.88rem; font-weight: 600; color: #fff;">
                    {username}
                </div>
                <div style="font-size: 0.75rem; color: #A5D6A7; margin-top: 0.1rem;">
                    {role}{(' · ' + province) if province else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Logout button ─────────────────────────────────────
        st.markdown("<div style='padding: 0 0.75rem; margin-top: 0.25rem;'>", unsafe_allow_html=True)


        if st.button("Sign Out", use_container_width=True, key="sidebar_logout"):
            api.logout()
            st.rerun()
            key="sidebar_logout"

        st.markdown("</div>", unsafe_allow_html=True)

    return page