import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data import generate_schools, get_national_summary
from components.cards import (
    metric_card, section_header, divider, info_box, alert_banner, page_footer, risk_badge
)

PLOT_COLORS = {
    "High":   "#DC2626",
    "Medium": "#F59E0B",
    "Low":    "#40916C",
}

FONT = "Inter, sans-serif"


def render():
    df     = generate_schools(120)
    stats  = get_national_summary(df)

    section_header(
        "National Overview",
        "Real-time snapshot of teacher attrition risk across all provinces · Academic Year 2024/25"
    )

    # ── Alert banner ──
    alert_banner(
        f"<strong>{stats['high_risk']} schools</strong> are currently flagged as High Risk across "
        f"{stats['provinces_flagged']} provinces. Immediate policy attention is recommended for "
        f"Western, Luapula, and Muchinga provinces."
    )

    # ── KPI row ──
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_card("Total Schools Monitored", stats["total_schools"])
    with c2: metric_card("High Risk Schools",   stats["high_risk"],   f"{stats['high_pct']}% of total", accent="high")
    with c3: metric_card("Medium Risk Schools", stats["medium_risk"],  accent="medium")
    with c4: metric_card("Low Risk Schools",    stats["low_risk"],     accent="low")
    with c5: metric_card("Avg. Attrition Rate", f"{stats['avg_attrition']}%", "2021 → 2022")

    divider()

    # ── Row 2: Donut + Province bar ──
    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        st.markdown('<div class="section-label">Risk Distribution</div>', unsafe_allow_html=True)
        risk_counts = df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Schools"]
        risk_counts["Risk Level"] = pd.Categorical(
            risk_counts["Risk Level"], categories=["High", "Medium", "Low"], ordered=True
        )
        risk_counts = risk_counts.sort_values("Risk Level")

        fig_donut = go.Figure(go.Pie(
            labels=risk_counts["Risk Level"],
            values=risk_counts["Schools"],
            hole=0.58,
            marker_colors=[PLOT_COLORS[r] for r in risk_counts["Risk Level"]],
            textinfo="percent",
            textfont=dict(size=13, family=FONT),
            hovertemplate="<b>%{label}</b><br>%{value} schools<extra></extra>",
        ))
        fig_donut.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(font=dict(family=FONT, size=12)),
            height=280,
            annotations=[dict(
                text=f"<b>{stats['total_schools']}</b><br><span style='font-size:10px'>Schools</span>",
                x=0.5, y=0.5, font_size=18, font_family=FONT, showarrow=False
            )],
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown('<div class="section-label">High-Risk Schools by Province</div>', unsafe_allow_html=True)
        high_risk = (
            df[df["risk_level"] == "High"]
            .groupby("province")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=True)
        )
        fig_bar = go.Figure(go.Bar(
            x=high_risk["count"],
            y=high_risk["province"],
            orientation="h",
            marker_color="#DC2626",
            text=high_risk["count"],
            textposition="outside",
            textfont=dict(family=FONT, size=12),
            hovertemplate="<b>%{y}</b><br>%{x} high-risk schools<extra></extra>",
        ))
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=10, r=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0", gridwidth=1,
                       title="", tickfont=dict(family=FONT, size=11)),
            yaxis=dict(title="", tickfont=dict(family=FONT, size=12)),
            height=300,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    divider()

    # ── Row 3: Province heat table + recent flags ──
    col_a, col_b = st.columns([1.5, 1])

    with col_a:
        st.markdown('<div class="section-label">Province Summary</div>', unsafe_allow_html=True)
        prov_summary = (
            df.groupby("province")
            .agg(
                Total=("school_id", "count"),
                High=("risk_level", lambda x: (x == "High").sum()),
                Medium=("risk_level", lambda x: (x == "Medium").sum()),
                Low=("risk_level", lambda x: (x == "Low").sum()),
                Avg_Attrition=("attrition_pct", "mean"),
            )
            .reset_index()
            .rename(columns={"province": "Province", "Avg_Attrition": "Avg Attrition (%)"})
            .sort_values("High", ascending=False)
        )
        prov_summary["Avg Attrition (%)"] = prov_summary["Avg Attrition (%)"].round(1)
        st.dataframe(
            prov_summary,
            use_container_width=True,
            hide_index=True,
            height=300,
            column_config={
                "High":   st.column_config.NumberColumn("High Risk", help="Schools at high risk"),
                "Medium": st.column_config.NumberColumn("Medium Risk"),
                "Low":    st.column_config.NumberColumn("Low Risk"),
            }
        )

    with col_b:
        st.markdown('<div class="section-label">Recently Flagged Schools</div>', unsafe_allow_html=True)
        recent_flags = (
            df[df["risk_level"] == "High"]
            .sort_values("risk_score", ascending=False)
            .head(6)[["school_name", "district", "risk_score"]]
        )
        for _, row in recent_flags.iterrows():
            st.markdown(f"""
            <div style="padding:0.65rem 0.9rem; margin-bottom:0.5rem; background:#fff;
                        border:1px solid #E2E8F0; border-left:3px solid #DC2626;
                        border-radius:6px; font-size:0.82rem;">
                <div style="font-weight:600; color:#0F172A; margin-bottom:0.15rem;">
                    {row['school_name']}
                </div>
                <div style="color:#64748B; display:flex; justify-content:space-between;">
                    <span>{row['district']}</span>
                    <span style="font-weight:600; color:#DC2626;">Score: {row['risk_score']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    divider()

    info_box(
        "<strong>About the model:</strong> Risk scores are generated by an XGBoost classifier "
        "trained on MoE Education Statistics Bulletin data (2009–2022). A school is classified "
        "as High Risk when its predicted probability of a &gt;15% teacher headcount decline "
        "exceeds 0.65. SHAP values are available on the Model Insights page."
    )

    page_footer()