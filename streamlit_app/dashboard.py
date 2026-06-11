"""
Teacher Attrition Early Warning System — Streamlit Dashboard
Authors: Florence Kabeya  | African Leadership University

Run with:  streamlit run streamlit_app/dashboard.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# ── Config ─────────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="Teacher Attrition EWS",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.risk-high  { background:#FFEBEE; border-left:5px solid #F44336; padding:10px; border-radius:4px; }
.risk-low   { background:#E8F5E9; border-left:5px solid #4CAF50; padding:10px; border-radius:4px; }
.metric-card{ background:#F5F5F5; border-radius:8px; padding:16px; text-align:center; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Coat_of_arms_of_Zambia.svg/120px-Coat_of_arms_of_Zambia.svg.png", width=80)
    st.title("EWS Navigation")
    page = st.radio("Go to", [
        " Dashboard Overview",
        " Single School Prediction",
        " Batch Prediction",
        " Upload Bulletin Data",
        "ℹ About",
    ])
    st.divider()
    st.caption("Teacher Attrition EWS v1.0")
    st.caption("African Leadership University")
    st.caption("MoE Education Statistics Bulletin 2022")


# ── Helper functions ──────────────────────────────────────────────────────────

def api_get(endpoint: str):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def api_post(endpoint: str, payload: dict):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API. Make sure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def risk_badge(label: str, score: float) -> str:
    if label == "high_risk":
        return f'<div class="risk-high">🔴 HIGH RISK — {score:.0%} probability</div>'
    return f'<div class="risk-low">🟢 NOT AT RISK — {score:.0%} probability</div>'

def shap_bar_chart(shap_entries: list):
    if not shap_entries:
        return
    df = pd.DataFrame(shap_entries)
    df["color"] = df["shap_value"].apply(lambda x: "#F44336" if x > 0 else "#4CAF50")
    df = df.sort_values("shap_value", key=abs, ascending=True)
    fig = px.bar(
        df, x="shap_value", y="feature",
        orientation="h",
        color="color",
        color_discrete_map="identity",
        labels={"shap_value": "SHAP Value (impact on risk)", "feature": "Feature"},
        title="SHAP Feature Attributions — Factors Driving This Prediction",
    )
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)


# ── Page: Dashboard Overview ──────────────────────────────────────────────────
if page == " Dashboard Overview":
    st.title(" Teacher Attrition Early Warning System")
    st.caption("Chongwe District, Lusaka Province — Decision Support Prototype")
    st.divider()

    # Health check
    health = api_get("/health".replace("/api/v1", "")) or {}
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("API Status",    "Online" if health.get("status") == "ok" else "Offline")
    col2.metric("Model Loaded",  "Yes" if health.get("model_loaded") else "No")
    col3.metric("DB Connected",  "Yes" if health.get("db_connected") else "No")
    col4.metric("API Version",   health.get("api_version", "—"))

    st.divider()
    st.subheader("How to use this dashboard")
    st.markdown("""
    1. **Single School Prediction** — enter feature values for one school and see the risk score + SHAP explanation.
    2. **Batch Prediction** — paste or upload a table of schools and receive a ranked risk list.
    3. **Upload Bulletin Data** — upload a MoE-format CSV to refresh all predictions in the database.

    > This tool is a **decision support aid**. Risk scores surface signals for district officers to
    > investigate — they do not make or recommend employment decisions about individual teachers.
    """)

    st.info(
        "**Primary dataset:** MoE Education Statistics Bulletin 2022 | "
        "**Model:** XGBoost (RandomizedSearchCV, 5-fold CV, primary metric: Recall)"
    )


# ── Page: Single School Prediction ───────────────────────────────────────────
elif page == " Single School Prediction":
    st.title(" Single School Risk Prediction")
    st.caption("Enter school-level feature values to generate an attrition risk score.")

    with st.form("predict_form"):
        c1, c2 = st.columns(2)
        school_code       = c1.text_input("School Code",        value="CHO_001")
        is_secondary      = c2.selectbox("Education Level",     [0, 1], format_func=lambda x: "Primary" if x == 0 else "Secondary")
        ptr_deviation     = c1.number_input("PTR Deviation (z-score)", value=0.45, step=0.01, format="%.3f",
                                            help="How far this school's PTR is from the national mean")
        qualification_gap = c2.number_input("Qualification Gap (0–1)", value=0.22, min_value=0.0, max_value=1.0, step=0.01,
                                            help="Proportion of teachers without full qualifications")
        rural_isolation   = c1.number_input("Rural Isolation Index (0–1)", value=0.74, min_value=0.0, max_value=1.0, step=0.01,
                                            help="Proportion of rural schools in the province")
        teacher_delta_pct = c2.number_input("YoY Teacher Change (%)", value=-18.5, step=0.1,
                                            help="Negative = teacher headcount declined")
        enrolment_growth  = c1.number_input("Enrolment Growth (%)", value=4.2, step=0.1)
        pressure_gap      = c2.number_input("Pressure Gap", value=5.8, step=0.1,
                                            help="Enrolment growth minus teacher growth")
        attrition_rate    = c1.number_input("Attrition Rate (%)", value=7.2, min_value=0.0, step=0.1)

        submitted = st.form_submit_button("Run Prediction", type="primary")

    if submitted:
        payload = {
            "school_code":       school_code,
            "ptr_deviation":     ptr_deviation,
            "qualification_gap": qualification_gap,
            "rural_isolation":   rural_isolation,
            "teacher_delta_pct": teacher_delta_pct,
            "enrolment_growth":  enrolment_growth,
            "pressure_gap":      pressure_gap,
            "attrition_rate":    attrition_rate,
            "is_secondary":      is_secondary,
        }
        with st.spinner("Running prediction..."):
            result = api_post("/predict", payload)

        if result:
            st.markdown(risk_badge(result["risk_label"], result["risk_score"]), unsafe_allow_html=True)
            st.divider()

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Risk Score",      f"{result['risk_score']:.3f}")
            col_b.metric("Confidence",      f"{result['confidence_pct']:.1f}%")
            col_c.metric("Model Version",   result["model_version"])

            st.info(f"**Plain-language summary:** {result['plain_language_summary']}")

            st.subheader("SHAP Explanation")
            shap_bar_chart(result.get("shap_explanation", []))

            with st.expander("Raw API response"):
                st.json(result)


# ── Page: Batch Prediction ────────────────────────────────────────────────────
elif page == " Batch Prediction":
    st.title(" Batch Risk Prediction")
    st.caption("Paste school data or use the sample below. Up to 200 records.")

    sample = [
        {"school_code":"LUS_001","ptr_deviation":0.45,"qualification_gap":0.22,"rural_isolation":0.74,
         "teacher_delta_pct":-18.5,"enrolment_growth":4.2,"pressure_gap":5.8,"attrition_rate":7.2,"is_secondary":0},
        {"school_code":"LUS_002","ptr_deviation":-0.3,"qualification_gap":0.10,"rural_isolation":0.40,
         "teacher_delta_pct":2.1,"enrolment_growth":1.5,"pressure_gap":-0.6,"attrition_rate":4.1,"is_secondary":0},
        {"school_code":"LUS_003","ptr_deviation":1.8,"qualification_gap":0.35,"rural_isolation":0.90,
         "teacher_delta_pct":-22.0,"enrolment_growth":6.0,"pressure_gap":9.0,"attrition_rate":10.5,"is_secondary":1},
    ]

    if st.button("Load sample data"):
        st.session_state["batch_records"] = sample

    records = st.session_state.get("batch_records", sample)
    st.json(records[:2])

    if st.button("Run Batch Prediction", type="primary"):
        with st.spinner(f"Predicting {len(records)} schools..."):
            result = api_post("/predict/batch", {"records": records})

        if result:
            st.success(f"Processed {result['total']} schools — {result['high_risk_count']} flagged HIGH RISK")

            preds = result["predictions"]
            df_pred = pd.DataFrame([{
                "School Code":  p["school_code"],
                "Risk Label":   p["risk_label"].replace("_", " ").title(),
                "Risk Score":   round(p["risk_score"], 3),
                "Confidence %": p["confidence_pct"],
            } for p in preds])

            def color_risk(row):
                if row["Risk Label"] == "High Risk":
                    return ["background-color:#FFEBEE"]*len(row)
                return ["background-color:#E8F5E9"]*len(row)

            st.dataframe(
                df_pred.style.apply(color_risk, axis=1),
                use_container_width=True
            )

            fig = px.bar(
                df_pred, x="School Code", y="Risk Score",
                color="Risk Label",
                color_discrete_map={"High Risk": "#F44336", "Not At Risk": "#4CAF50"},
                title="Risk Scores — Ranked by School",
            )
            fig.add_hline(y=0.5, line_dash="dash", line_color="orange", annotation_text="Decision threshold (0.5)")
            st.plotly_chart(fig, use_container_width=True)


# ── Page: Upload Bulletin Data ────────────────────────────────────────────────
elif page == " Upload Bulletin Data":
    st.title(" Upload MoE Bulletin CSV")
    st.caption("Upload a CSV to refresh risk predictions for all schools in the dataset.")

    st.markdown("""
    **Required CSV columns:**
    `school_code`, `province`, `district`, `level`, `year`, `teachers`, `teachers_prev`,
    `ptr`, `enrolment`, `enrolment_prev`, `qualified_ratio`, `attrition_est`,
    `schools_rural`, `schools_urban`
    """)

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded and st.button("Upload & Run Predictions", type="primary"):
        with st.spinner("Processing..."):
            r = requests.post(
                f"{API_BASE}/upload",
                files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")},
                timeout=60,
            )
        if r.status_code == 200:
            data = r.json()
            st.success(data["message"])
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows Processed",  data["rows_processed"])
            col2.metric("High Risk Flagged", data["high_risk_count"])
            col3.metric("Model Version",   data["model_version"])
        else:
            st.error(f"Upload failed: {r.text}")


# ── Page: About ───────────────────────────────────────────────────────────────
elif page == " About":
    st.title("About This System")
    st.markdown("""
    ### Teacher Attrition Early Warning System (EWS)

    This prototype was developed as a BSc Software Engineering capstone project at
    **African Leadership University** by Florence Kabeya and Elvira Khwatenge.

    **Purpose:** Provide Chongwe District education officers with a data-driven tool to
    identify schools at elevated teacher attrition risk before vacancies become critical,
    supporting the 2024–2029 MoE Education Sector Partnership Compact.

    **Dataset:** MoE Education Statistics Bulletin 2022 (all 10 provinces) +
    UNESCO Institute for Statistics time-series 2010–2022.

    **Model:** XGBoost classifier (primary), benchmarked against Logistic Regression,
    Random Forest, Decision Tree, and SVM. Primary metric: Recall (minimise false negatives).
    SHAP values provide feature-level explanations for every prediction.

    **Limitations:** This is a decision-support prototype, not a production system.
    The attrition risk label is a proxy derived from year-on-year teacher headcount changes.
    Results should be interpreted alongside local contextual knowledge.

    **Tech stack:** Python 3.11 · FastAPI · MySQL · Streamlit · XGBoost · SHAP · MLflow · Render
    """)