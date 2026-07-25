import streamlit as st
import pandas as pd

from api_client import get_province_predictions

from components.cards import (
    metric_card,
    section_header,
    divider,
    alert_banner,
    page_footer,
)


def render():

    # ==================================
    # Load prediction data
    # ==================================

    provinces = get_province_predictions()

    df = pd.DataFrame(provinces)


    if df.empty:
        st.warning(
            "No province prediction data available. "
            "Please run model inference from the admin controls."
        )
        return


    section_header(
        "At-Risk Provinces",
        "Ranked province-level teacher attrition risk assessment based on XGBoost predictions"
    )


    # ==================================
    # Filters
    # ==================================

    col1, col2, col3 = st.columns([1.5,1.5,1])


    with col1:

        province_options = [
            "All Provinces"
        ] + sorted(
            df["province"].unique()
        )

        selected_province = st.selectbox(
            "Province",
            province_options
        )


    with col2:

        risk_options = [
            "All",
            "high_risk",
            "not_at_risk"
        ]

        selected_risk = st.selectbox(
            "Risk Level",
            risk_options
        )


    with col3:

        years = [
            "All Years"
        ] + sorted(
            df["year"].unique(),
            reverse=True
        )

        selected_year = st.selectbox(
            "Prediction Year",
            years
        )



    # ==================================
    # Apply filters
    # ==================================

    filtered = df.copy()


    if selected_province != "All Provinces":

        filtered = filtered[
            filtered["province"]
            ==
            selected_province
        ]


    if selected_risk != "All":

        filtered = filtered[
            filtered["risk_label"]
            ==
            selected_risk
        ]


    if selected_year != "All Years":

        filtered = filtered[
            filtered["year"]
            ==
            selected_year
        ]



    filtered = filtered.sort_values(
        "risk_score",
        ascending=False
    )


    divider()



    # ==================================
    # KPI SUMMARY
    # ==================================

    total = len(filtered)

    high_risk = (
        filtered["risk_label"]
        ==
        "high_risk"
    ).sum()


    stable = (
        filtered["risk_label"]
        ==
        "not_at_risk"
    ).sum()


    avg_risk = (
        filtered["risk_score"]
        .mean()
    )


    c1,c2,c3,c4 = st.columns(4)


    with c1:

        metric_card(
            "Provinces Shown",
            total,
            "Current selection",
            accent="low"
        )


    with c2:

        metric_card(
            "High Risk",
            high_risk,
            f"{round((high_risk/total)*100,1) if total else 0}% of selection",
            accent="high"
        )


    with c3:

        metric_card(
            "Stable Provinces",
            stable,
            f"{round((stable/total)*100,1) if total else 0}% of selection",
            accent="low"
        )


    with c4:

        metric_card(
            "Average Risk Score",
            round(avg_risk,2) if not pd.isna(avg_risk) else 0,
            "XGBoost probability",
            accent="medium"
        )



    divider()



    # ==================================
    # Alert
    # ==================================

    if high_risk > 0:

        alert_banner(
            f"""
            <strong>{high_risk} province(s)</strong> are classified as 
            high risk in the current selection.
            Priority review is recommended for targeted teacher retention interventions.
            """
        )



    # ==================================
    # Risk Register
    # ==================================

    st.markdown(
        '<div class="section-label">Province Risk Register</div>',
        unsafe_allow_html=True
    )


    display_df = filtered[
        [
            "province",
            "year",
            "risk_score",
            "risk_label",
            "confidence_pct",
            "ptr_primary_calc",
            "teacher_growth_rate",
            "recruitment_gap",
            "rural_school_pct",
            "attrition_proxy_rate"
        ]
    ].copy()



    display_df.columns = [

        "Province",
        "Year",
        "Risk Score",
        "Risk Level",
        "Confidence %",
        "PTR",
        "Teacher Growth %",
        "Recruitment Gap",
        "Rural School %",
        "Attrition Proxy"

    ]



    st.dataframe(

        display_df,

        width="stretch",

        hide_index=True,

        height=450,

        column_config={

            "Risk Score":

                st.column_config.ProgressColumn(

                    "Risk Score",

                    min_value=0,

                    max_value=1,

                    format="%.3f"

                ),


            "Confidence %":

                st.column_config.NumberColumn(

                    format="%.2f"

                ),


            "PTR":

                st.column_config.NumberColumn(

                    format="%.2f"

                )

        }

    )



    st.caption(
        f"Showing {len(filtered)} province prediction(s) · Sorted by highest risk score"
    )



    divider()



    # ==================================
    # Export
    # ==================================

    csv = display_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(

        label="Export Province Risk Report",

        data=csv,

        file_name="ews_province_risk_report.csv",

        mime="text/csv"

    )



    page_footer()


