"""
Administration page for the Rural Teacher Attrition Early Warning System.

Restricted functionality available only to Data Administrators.

Features
--------
• Run a prediction for a single province
• Upload a new Ministry of Education dataset
"""

import json

import pandas as pd
import streamlit as st

from api_client import (
    get_current_user,
    run_prediction,
    upload_bulletin,
)

from components.cards import (
    divider,
    info_box,
    metric_card,
    page_footer,
    section_header,
)


PROVINCES = [
    "Central",
    "Copperbelt",
    "Eastern",
    "Luapula",
    "Lusaka",
    "Muchinga",
    "North-Western",
    "Northern",
    "Southern",
    "Western",
]


def render():
    """
    Render the Administration page.
    """

    # ==========================================================
    # Access Control
    # ==========================================================

    user = get_current_user()

    if not user or user.get("role") != "data_admin":
        st.error("Access denied.")
        st.stop()

    # ==========================================================
    # Header
    # ==========================================================

    section_header(
        "Administration",
        "Administrative tools for data management and model execution."
    )

    # ==========================================================
    # Province Prediction
    # ==========================================================

    st.markdown(
        '<div class="section-label">Run Province Prediction</div>',
        unsafe_allow_html=True,
    )

    info_box(
        """
        Generate a new teacher attrition prediction for a single
        province using the latest available dataset.
        """
    )

    c1, c2 = st.columns(2)

    with c1:
        province = st.selectbox(
            "Province",
            PROVINCES,
        )

    with c2:
        year = st.number_input(
            "Prediction Year",
            min_value=2010,
            max_value=2035,
            value=2025,
            step=1,
        )

    if st.button(
        "Run Province Prediction",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner("Running prediction..."):

            # assumes backend endpoint now accepts year
            result = run_prediction(
                province,
                year,
            )

        if result:

            st.success("Prediction completed successfully.")

            divider()

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                metric_card(
                    "Risk Score",
                    f"{result['risk_score']:.3f}",
                    "Prediction",
                    accent="high"
                    if result["risk_label"] == "high_risk"
                    else "low",
                )

            with c2:
                metric_card(
                    "Risk Label",
                    result["risk_label"]
                    .replace("_", " ")
                    .title(),
                    "Classification",
                    accent="high"
                    if result["risk_label"] == "high_risk"
                    else "low",
                )

            with c3:
                metric_card(
                    "Confidence",
                    f"{result['confidence_pct']}%",
                    "Model confidence",
                    accent="medium",
                )

            with c4:
                metric_card(
                    "Model",
                    result["model_version"],
                    f"Year {result['year']}",
                    accent="low",
                )

            divider()

            st.markdown(
                "### Prediction Details"
            )

            details = pd.DataFrame(
                {
                    "Metric": [
                        "Primary PTR",
                        "Teacher Growth",
                        "Recruitment Gap",
                        "Rural School %",
                        "Attrition Proxy",
                    ],
                    "Value": [
                        result["ptr_primary_calc"],
                        result["teacher_growth_rate"],
                        result["recruitment_gap"],
                        result["rural_school_pct"],
                        result["attrition_proxy_rate"],
                    ],
                }
            )

            st.dataframe(
                details,
                use_container_width=True,
                hide_index=True,
            )

            divider()

            st.markdown(
                "### SHAP Feature Contributions"
            )

            shap = json.loads(
                result["shap_json"]
            )

            shap_df = (
                pd.DataFrame(
                    {
                        "Feature": shap.keys(),
                        "SHAP Value": shap.values(),
                    }
                )
                .sort_values(
                    "SHAP Value",
                    ascending=False,
                )
            )

            st.bar_chart(
                shap_df.set_index("Feature")
            )

            strongest = shap_df.iloc[0]

            info_box(
                f"""
                <strong>Model Explanation</strong>

                <br><br>

                This prediction is explained using <strong>SHAP (SHapley Additive Explanations)</strong>, which identifies the factors that had the greatest influence on the model's decision.

                <br><br>

                For <strong>{province}</strong>, the strongest contributing factor was
                <strong>{strongest['Feature']}</strong>, with a SHAP value of
                <strong>{strongest['SHAP Value']:+.3f}</strong>.

                <br><br>

                <strong>How to interpret SHAP values:</strong>

                <ul style="margin-top:8px; margin-bottom:8px;">
                    <li><strong>Positive</strong> SHAP values increase the predicted teacher attrition risk.</li>
                    <li><strong>Negative</strong> SHAP values reduce the predicted teacher attrition risk.</li>
                    <li>Features with larger absolute SHAP values have a greater influence on the model's prediction.</li>
                </ul>

                These explanations improve transparency by showing why the model classified the selected province as <strong>{result['risk_label'].replace('_', ' ').title()}</strong>, allowing decision-makers to interpret the prediction with confidence rather than treating it as a black-box result.
            """
            )

    divider()

    # ==========================================================
    # Upload Dataset
    # ==========================================================

    st.markdown(
        '<div class="section-label">Upload Education Dataset</div>',
        unsafe_allow_html=True,
    )

    info_box(
        f"""
        Upload the latest Ministry of Education Education Statistics
        Bulletin in CSV format.

        Uploaded data replaces the existing provincial dataset and
        becomes the source for future model predictions.
        """
    )

    uploaded_file = st.file_uploader(
        "CSV File",
        type=["csv"],
    )

    if uploaded_file:

        st.write(f"Selected file: **{uploaded_file.name}**")

        if st.button(
            "Upload Dataset",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner("Uploading dataset..."):

                result = upload_bulletin(
                    uploaded_file
                )

            if result:

                st.success(
                    "Dataset uploaded successfully."
                )

                if "rows_imported" in result:

                    metric_card(
                        "Rows Imported",
                        result["rows_imported"],
                        "Records loaded",
                        accent="low",
                    )

                info_box(
                    f"""
                    <strong>Dataset Uploaded Successfully</strong>

                    <br><br>

                    The new Ministry of Education dataset has been stored and is ready for analysis.

                    <br><br>

                    You can now generate predictions by:
                    <ul style="margin-top:8px; margin-bottom:8px;">
                        <li>Running a <strong>Province Prediction</strong> on this page for an individual province, or</li>
                        <li>Running a <strong>National Risk Assessment</strong> from the Overview page to update predictions for all provinces.</li>
                    </ul>

                    Newly generated predictions will use the uploaded dataset and will automatically update the associated risk scores and SHAP explanations.
                """
                )

            else:

                st.error(
                    "Dataset upload failed."
                )

    page_footer()