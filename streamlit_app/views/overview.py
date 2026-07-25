from scipy import stats
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from api_client import (
    get_national_summary,
    get_province_summary,
    run_all_predictions,
    get_current_user,
)

from components.cards import (
    metric_card,
    section_header,
    divider,
    info_box,
    alert_banner,
    page_footer,
)


PLOT_COLORS = {
    "high_risk": "#DC2626",
    "not_at_risk": "#40916C",
}

FONT = "Inter, sans-serif"


def render():

    # ==============================
    # Load API data
    # ==============================

    stats = get_national_summary()
    provinces = get_province_summary()

    df = pd.DataFrame(provinces)


    if df.empty:
        st.warning(
            "No prediction data available. "
            "Please run ML inference from the admin panel."
        )
        return


    section_header(
        "National Overview",
        "Province-level teacher attrition risk assessment based on "
        "Ministry of Education statistics indicators"
    )


    # ==============================
    # Admin inference button
    # ==============================

    user = get_current_user()

    if user and user.get("role") == "data_admin":

        with st.expander("Model Controls"):

            st.write(
                "Trigger the latest XGBoost inference for all provinces."
            )

            if st.button(
                "Run National Risk Assessment",
                type="primary",
                key="overview_run_national_risk"
            ):

                result = run_all_predictions()

                if result:
                    st.success(
                        f"Completed predictions for "
                        f"{result.get('inserted',0)} provinces."
                    )
                    st.rerun()



    # ==============================
    # Alert banner
    # ==============================

    high_count = stats.get("high_risk", 0)
    not_at_risk_count = stats.get("not_at_risk", 0)
    total = stats.get("total_provinces", 0)

    high_risk_pct = (
        round((high_count / total) * 100, 1)
        if total > 0 else 0
   )

    not_at_risk_pct = (
        round((not_at_risk_count / total) * 100, 1)
        if total > 0 else 0
    )

    alert_banner(
        f"""
        <strong>{high_count} provinces</strong> are currently classified "
        "as High Risk out of {total} assessed provinces.
        Priority intervention is recommended for provinces with elevated "
        "teacher attrition probability.
        """
    )


   # ==============================
   # KPI cards
   # ==============================





    c1, c2, c3, c4, c5 = st.columns(5)


    with c1:
        metric_card(
        "Provinces Analysed",
        total,
        f"Year {stats.get('prediction_year','')}",
        accent="low"
    )


    with c2:
        metric_card(
        "High Risk Provinces",
        high_count,
        f"{high_risk_pct}% of total",
        accent="high"
    )


    with c3:
        metric_card(
        "Stable Provinces",
        not_at_risk_count,
        f"{not_at_risk_pct}% of total",
        accent="low"
    )


    with c4:
        metric_card(
        "Average Risk Score",
        round(stats.get("avg_risk_score", 0), 2),
        "XGBoost probability",
        accent="medium"
    )


    with c5:
        metric_card(
        "Active Model",
        stats.get("active_model", "N/A"),
        "Current version",
        accent="low"
    )



    # ==============================
    # Risk distribution chart
    # ==============================


    left,right = st.columns([1,1.5])


    with left:

        st.markdown(
            '<div class="section-label">Risk Distribution</div>',
            unsafe_allow_html=True
        )


        counts = (
            df["risk_label"]
            .value_counts()
            .reset_index()
        )

        counts.columns=[
            "Risk",
            "Count"
        ]


        fig = go.Figure(
            go.Pie(
                labels=counts["Risk"],
                values=counts["Count"],
                hole=0.6,
                marker_colors=[
                    PLOT_COLORS.get(x,"#64748B")
                    for x in counts["Risk"]
                ],
                textinfo="percent"
            )
        )


        fig.update_layout(
            height=300,
            showlegend=True,
            margin=dict(
                t=10,
                b=10,
                l=10,
                r=10
            ),
            paper_bgcolor="rgba(0,0,0,0)"
        )


        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displayModeBar":False
            }
        )



    with right:

        st.markdown(
            '<div class="section-label">Province Risk Ranking</div>',
            unsafe_allow_html=True
        )


        ranking = (
            df.sort_values(
                "risk_score",
                ascending=True
            )
        )


        fig = go.Figure(
            go.Bar(
                x=ranking["risk_score"],
                y=ranking["province"],
                orientation="h",
                marker_color="#DC2626",
            )
        )


        fig.update_layout(
            height=320,
            xaxis_title="Risk Score",
            yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)"
        )


        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displayModeBar":False
            }
        )



    divider()



    # ==============================
    # Province ranking table
    # FR2
    # ==============================


    st.markdown(
        '<div class="section-label">Province Risk Assessment</div>',
        unsafe_allow_html=True
    )


    table = df[
        [
            "province",
            "risk_score",
            "risk_label",
            "confidence_pct",
            "ptr_primary_calc",
            "teacher_growth_rate",
            "attrition_proxy_rate"
        ]
    ].copy()


    table = table.sort_values(
        "risk_score",
        ascending=False
    )


    table.columns=[
        "Province",
        "Risk Score",
        "Risk Label",
        "Confidence %",
        "PTR",
        "Teacher Growth",
        "Attrition Proxy"
    ]


    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        height=350
    )



    divider()



    # ==============================
    # Highest risk provinces
    # ==============================


    st.markdown(
        '<div class="section-label">Highest Risk Provinces</div>',
        unsafe_allow_html=True
    )


    highest = (
        df.sort_values(
            "risk_score",
            ascending=False
        )
        .head(5)
    )


    for _,row in highest.iterrows():

        st.markdown(
            f"""
            <div style="
            padding:0.7rem;
            margin-bottom:0.5rem;
            background:#fff;
            border-left:4px solid #DC2626;
            border-radius:6px;
            border:1px solid #E2E8F0;
            ">

            <strong>{row['province']}</strong>

            <br>

            Risk Score:
            <span style="color:#DC2626;font-weight:bold">
            {row['risk_score']:.2f}
            </span>

            <br>

            Confidence:
            {row['confidence_pct']}%

            </div>
            """,
            unsafe_allow_html=True
        )



    divider()



    info_box(
        """
        <strong>About the model:</strong>
        Risk scores are generated using an XGBoost classifier trained on
        Ministry of Education statistics data.
        SHAP explanations are available on the Model Insights page.
        """
    )


    page_footer()



