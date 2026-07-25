import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from api_client import get_province_shap, get_health
from components.cards import (
    metric_card,
    section_header,
    divider,
    info_box,
    page_footer,
)

PROVINCES = [
    "Central", "Copperbelt", "Eastern", "Luapula", "Lusaka",
    "Muchinga", "North-Western", "Northern", "Southern", "Western"
]


def render():

    section_header(
        "Model Insights",
        "XGBoost model performance and SHAP-based explainability for province-level teacher attrition risk"
    )

    # Model performance summary
    health = get_health()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Model",
            health.get("active_model", "xgb_v1.0"),
            "Current version",
            accent="low"
        )

    with c2:
        metric_card(
            "LOPO AUC",
            f"{health.get('lopo_auc', 0):.4f}",
            "Mean ± 0.1693",
            accent="medium"
        )

    with c3:
        metric_card(
            "LOPO F1",
            "0.6310",
            "Mean ± 0.2600",
            accent="medium"
        )

    with c4:
        metric_card(
            "Training Period",
            "2009–2025",
            "Province data",
            accent="low"
        )

    divider()

    # Province selector
    selected_province = st.selectbox(
        "Select Province for SHAP Analysis",
        PROVINCES,
        index=4  # Default to Lusaka
    )

    # Load SHAP data from API
    shap_data = get_province_shap(selected_province)

    if not shap_data:
        st.warning(
            "No SHAP explanation data available for this province. "
            "Please ensure predictions have been generated."
        )
        return

    # Province summary
    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Risk Score",
            f"{shap_data['risk_score']:.3f}",
            f"Year {shap_data['year']}",
            accent="high" if shap_data["risk_label"] == "high_risk" else "low"
        )

    with c2:
        metric_card(
            "Risk Label",
            shap_data["risk_label"].replace("_", " ").title(),
            "Current classification",
            accent="high" if shap_data["risk_label"] == "high_risk" else "low"
        )

    with c3:
        metric_card(
            "Prediction Year",
            shap_data["year"],
            "Latest prediction",
            accent="low"
        )

    divider()

    # SHAP feature importance
    st.markdown(
        '<div class="section-label">SHAP Feature Contributions</div>',
        unsafe_allow_html=True
    )

    shap_values = shap_data["shap_values"]

    df_shap = pd.DataFrame({
        "Feature": list(shap_values.keys()),
        "SHAP Value": list(shap_values.values())
    })

    df_shap = df_shap.sort_values("SHAP Value")

    fig = go.Figure(go.Bar(
        x=df_shap["SHAP Value"],
        y=df_shap["Feature"],
        orientation="h",
        marker_color=[
            "#DC2626" if v > 0 else "#40916C"
            for v in df_shap["SHAP Value"]
        ],
        text=[f"{v:+.3f}" for v in df_shap["SHAP Value"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>SHAP: %{x:+.3f}<extra></extra>"
    ))

    fig.add_vline(x=0, line_color="#CBD5E1", line_width=1)

    fig.update_layout(
        height=420,
        margin=dict(t=20, b=20, l=0, r=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="SHAP Contribution to Risk",
            showgrid=True,
            gridcolor="#E2E8F0"
        ),
        yaxis=dict(title=""),
        showlegend=False
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    divider()

    # SHAP interpretation table
    st.markdown(
        '<div class="section-label">Feature Interpretation</div>',
        unsafe_allow_html=True
    )

    interpretation_df = df_shap.copy()
    interpretation_df["Direction"] = interpretation_df["SHAP Value"].apply(
        lambda x: "Increases Risk" if x > 0 else "Reduces Risk"
    )

    interpretation_df.columns = [
        "Feature",
        "SHAP Value",
        "Effect on Risk"
    ]

    st.dataframe(
        interpretation_df.sort_values("SHAP Value", ascending=False),
        width="stretch",
        hide_index=True,
        height=320
    )

    divider()

    # Explanation panel
    top_feature = df_shap.sort_values("SHAP Value", ascending=False).iloc[0]

    info_box(
        f"""
            <b>How to interpret this chart:</b>

            <br>

            • <b>Positive SHAP values (red)</b> increase the predicted attrition risk.

            <br>

            • <b>Negative SHAP values (green)</b> reduce the predicted attrition risk.

            <br>

            • The strongest contributor for this province is 
            <b>{top_feature['Feature']}</b>
            with a SHAP value of 
            <b>{top_feature['SHAP Value']:+.3f}</b>.

            <br><br>

            This provides transparency by showing policymakers why the XGBoost model 
            classified a province as high risk or not at risk.
        """
    )

    page_footer()


