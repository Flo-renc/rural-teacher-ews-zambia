import streamlit as st
import pandas as pd

from data import generate_schools, PROVINCES
from components.cards import section_header, divider, alert_banner, page_footer, risk_badge


def render():
    df = generate_schools(120)

    section_header(
        "At-Risk Schools",
        "Ranked list of schools by predicted attrition risk · Filter by province, district, or risk level"
    )

    # ── Filters ──
    col1, col2, col3, col4 = st.columns([1.4, 1.4, 1, 1])

    with col1:
        province_opts = ["All Provinces"] + sorted(PROVINCES)
        province      = st.selectbox("Province", province_opts)

    with col2:
        if province != "All Provinces":
            district_opts = ["All Districts"] + sorted(df[df["province"] == province]["district"].unique().tolist())
        else:
            district_opts = ["All Districts"] + sorted(df["district"].unique().tolist())
        district = st.selectbox("District", district_opts)

    with col3:
        risk_filter = st.selectbox("Risk Level", ["All", "High", "Medium", "Low"])

    with col4:
        school_type = st.selectbox("School Type", ["All", "Primary", "Secondary"])

    # ── Apply filters ──
    filtered = df.copy()
    if province  != "All Provinces": filtered = filtered[filtered["province"]    == province]
    if district  != "All Districts":  filtered = filtered[filtered["district"]   == district]
    if risk_filter != "All":          filtered = filtered[filtered["risk_level"] == risk_filter]
    if school_type != "All":          filtered = filtered[filtered["school_type"] == school_type]

    filtered = filtered.sort_values("risk_score", ascending=False)

    divider()

    # ── Summary strip ──
    n_high   = (filtered["risk_level"] == "High").sum()
    n_medium = (filtered["risk_level"] == "Medium").sum()
    n_low    = (filtered["risk_level"] == "Low").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Schools shown",   len(filtered))
    c2.metric("High Risk",       n_high,  delta=None)
    c3.metric("Medium Risk",     n_medium, delta=None)
    c4.metric("Low Risk",        n_low,   delta=None)

    divider()

    if n_high > 0:
        alert_banner(
            f"<strong>{n_high} high-risk school(s)</strong> in current selection. "
            "Review model scores and SHAP explanations on the Model Insights page before "
            "issuing deployment recommendations."
        )

    # ── Table ──
    st.markdown('<div class="section-label">School Risk Register</div>', unsafe_allow_html=True)

    display_df = filtered[[
        "school_id", "school_name", "province", "district", "school_type",
        "risk_level", "risk_score", "teachers_2022", "teachers_2023",
        "attrition_pct", "pupil_teacher_ratio"
    ]].rename(columns={
        "school_id":          "ID",
        "school_name":        "School Name",
        "province":           "Province",
        "district":           "District",
        "school_type":        "Type",
        "risk_level":         "Risk Level",
        "risk_score":         "Risk Score",
        "teachers_2022":      "Teachers 2022",
        "teachers_2023":      "Teachers 2023",
        "attrition_pct":      "Attrition %",
        "pupil_teacher_ratio":"PTR",
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=480,
        column_config={
            "Risk Score": st.column_config.ProgressColumn(
                "Risk Score",
                min_value=0,
                max_value=1,
                format="%.3f",
                help="XGBoost predicted probability of >15% teacher headcount decline"
            ),
            "Attrition %": st.column_config.NumberColumn("Attrition %", format="%.1f%%"),
            "PTR":         st.column_config.NumberColumn("Pupil:Teacher", format="%.1f"),
            "Risk Level":  st.column_config.TextColumn("Risk Level"),
        }
    )

    st.caption(f"Showing {len(filtered)} of 120 schools · Sorted by risk score (highest first)")

    divider()

    # ── Download ──
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export table as CSV",
        data=csv,
        file_name="ews_at_risk_schools.csv",
        mime="text/csv",
    )

    page_footer()