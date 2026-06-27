import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data import generate_trend_data, generate_schools, PROVINCES
from components.cards import section_header, divider, info_box, page_footer

FONT = "Inter, sans-serif"

GREEN_PALETTE = [
    "#1B4332", "#2D6A4F", "#40916C", "#52B788",
    "#74C69D", "#95D5B2", "#B7E4C7", "#D8F3DC",
    "#A7C957", "#386641",
]


def render():
    df_trend   = generate_trend_data()
    df_schools = generate_schools(120)

    section_header(
        "Teacher Trends",
        "Historical teacher headcount by province (2009–2025) · Source: MoE Education Statistics Bulletin"
    )

    tab1, tab2, tab3 = st.tabs(["National Trend", "Province Comparison", "Attrition Distribution"])

    # ── Tab 1: National aggregate line ──
    with tab1:
        national = (
            df_trend.groupby("year")["teachers"]
            .sum()
            .reset_index()
            .rename(columns={"teachers": "Total Teachers"})
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=national["year"],
            y=national["Total Teachers"],
            mode="lines+markers",
            line=dict(color="#2D6A4F", width=2.5),
            marker=dict(size=5, color="#2D6A4F"),
            fill="tozeroy",
            fillcolor="rgba(64,145,108,0.08)",
            name="National total",
            hovertemplate="<b>%{x}</b><br>%{y:,} teachers<extra></extra>",
        ))
        fig.update_layout(
            height=360,
            margin=dict(t=20, b=20, l=0, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=False,
                tickfont=dict(family=FONT, size=11),
                title="",
            ),
            yaxis=dict(
                showgrid=True, gridcolor="#E2E8F0", gridwidth=1,
                tickfont=dict(family=FONT, size=11),
                title="Total Teachers",
                titlefont=dict(family=FONT, size=12),
            ),
            hoverlabel=dict(font_family=FONT),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        info_box(
            "National teacher numbers include all provinces across both primary and secondary "
            "levels. Dips between 2015 and 2018 correspond to a freeze on teacher recruitment "
            "during fiscal consolidation. Data from Bulletin 2025 (2009–2025)."
        )

    # ── Tab 2: Province comparison multi-line ──
    with tab2:
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_provinces = st.multiselect(
                "Select provinces",
                options=sorted(PROVINCES),
                default=["Western", "Luapula", "Lusaka", "Copperbelt"],
            )

        with col2:
            if not selected_provinces:
                st.info("Select at least one province to display trends.")
            else:
                filtered = df_trend[df_trend["province"].isin(selected_provinces)]
                fig2 = go.Figure()
                for i, prov in enumerate(selected_provinces):
                    pdata = filtered[filtered["province"] == prov]
                    fig2.add_trace(go.Scatter(
                        x=pdata["year"],
                        y=pdata["teachers"],
                        mode="lines+markers",
                        name=prov,
                        line=dict(color=GREEN_PALETTE[i % len(GREEN_PALETTE)], width=2),
                        marker=dict(size=4),
                        hovertemplate=f"<b>{prov}</b><br>%{{x}}: %{{y:,}} teachers<extra></extra>",
                    ))
                fig2.update_layout(
                    height=380,
                    margin=dict(t=20, b=20, l=0, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, tickfont=dict(family=FONT, size=11), title=""),
                    yaxis=dict(
                        showgrid=True, gridcolor="#E2E8F0",
                        tickfont=dict(family=FONT, size=11), title="Teachers"
                    ),
                    legend=dict(font=dict(family=FONT, size=12)),
                    hoverlabel=dict(font_family=FONT),
                )
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Tab 3: Attrition distribution ──
    with tab3:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-label">Attrition % Distribution</div>', unsafe_allow_html=True)
            fig3 = px.histogram(
                df_schools,
                x="attrition_pct",
                nbins=25,
                color_discrete_sequence=["#40916C"],
                labels={"attrition_pct": "Attrition Rate (%)"},
            )
            fig3.add_vline(
                x=15, line_dash="dash", line_color="#DC2626", line_width=1.5,
                annotation_text="15% threshold", annotation_font_size=11,
                annotation_font_family=FONT,
            )
            fig3.update_layout(
                height=320,
                margin=dict(t=10, b=10, l=0, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont=dict(family=FONT, size=11)),
                yaxis=dict(showgrid=True, gridcolor="#E2E8F0", tickfont=dict(family=FONT, size=11)),
                showlegend=False,
                bargap=0.05,
            )
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        with col_b:
            st.markdown('<div class="section-label">Avg Attrition by Province</div>', unsafe_allow_html=True)
            prov_attr = (
                df_schools.groupby("province")["attrition_pct"]
                .mean()
                .reset_index()
                .sort_values("attrition_pct", ascending=True)
            )
            fig4 = go.Figure(go.Bar(
                x=prov_attr["attrition_pct"],
                y=prov_attr["province"],
                orientation="h",
                marker_color=[
                    "#DC2626" if v > 20 else "#F59E0B" if v > 10 else "#40916C"
                    for v in prov_attr["attrition_pct"]
                ],
                text=[f"{v:.1f}%" for v in prov_attr["attrition_pct"]],
                textposition="outside",
                textfont=dict(family=FONT, size=11),
                hovertemplate="<b>%{y}</b><br>Avg attrition: %{x:.1f}%<extra></extra>",
            ))
            fig4.update_layout(
                height=320,
                margin=dict(t=10, b=10, l=0, r=50),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#E2E8F0", title="", tickfont=dict(family=FONT, size=11)),
                yaxis=dict(title="", tickfont=dict(family=FONT, size=11)),
                showlegend=False,
            )
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    page_footer()