import streamlit as st
import api_client as api


def render():
    st.markdown("""
    <div style="max-width:420px; margin:4rem auto 0 auto;">
        <div style="text-align:center; margin-bottom:2rem;">
            <div style="font-size:0.7rem; font-weight:700; letter-spacing:0.12em;
                        text-transform:uppercase; color:#2D6A4F; margin-bottom:0.5rem;">
                Ministry of Education · Zambia
            </div>
            <div style="font-size:1.6rem; font-weight:700; color:#0F172A; line-height:1.2;">
                Teacher Attrition<br>Early Warning System
            </div>
            <div style="font-size:0.85rem; color:#64748B; margin-top:0.5rem;">
                Sign in to access the dashboard
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]

    with col:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. florence.kabeya")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Signing in..."):
                    success = api.login(username, password)
                if success:
                    st.success("Signed in successfully.")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown("""
        <div style="text-align:center; margin-top:1.5rem; font-size:0.78rem; color:#94A3B8;">
            Contact your data administrator to create an account.
        </div>
        """, unsafe_allow_html=True)
