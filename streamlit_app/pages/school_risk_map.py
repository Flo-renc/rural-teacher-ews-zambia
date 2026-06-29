import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data import generate_schools, PROVINCES
from components.cards import section_header, divider, info_box, page_footer

FONT  = "Inter, sans-serif"
COLORS = {"High": "#DC2626", "Medium": "#F59E0B", "Low": "#40916C"}


def render():
    df = generate_schools(120)

    section_header(
        "School Risk Map",
        "Geographic distribution of teacher attrition risk across Zambia"
    )

    # ── Filters ──
    col1, col2, col3 = st.columns([1.2, 1.2, 1])
    with col1:
        province_opts = ["All Provinces"] + sorted(PROVINCES)
        province = st.selectbox("Filter by Province", province_opts)
    with col2:
        risk_filter = st.multiselect(
            "Risk Level", ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )
    with col3:
        school_type = st.selectbox("School Type", ["All", "Primary", "Secondary"])

    # ── Apply filters ──
    filtered = df.copy()
    if province    != "All Provinces": filtered = filtered[filtered["province"]    == province]
    if risk_filter:                    filtered = filtered[filtered["risk_level"].isin(risk_filter)]
    if school_type != "All":           filtered = filtered[filtered["school_type"] == school_type]

    divider()

    # ── Map ──
    st.markdown('<div class="section-label">Attrition Risk — School Locations</div>', unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No schools match the selected filters.")
    else:
        fig = go.Figure()

        for risk_level in ["High", "Medium", "Low"]:
            subset = filtered[filtered["risk_level"] == risk_level]
            if subset.empty:
                continue
            fig.add_trace(go.Scattermapbox(
                lat=subset["latitude"],
                lon=subset["longitude"],
                mode="markers",
                name=f"{risk_level} Risk",
                marker=dict(
                    size=subset["risk_score"] * 16 + 5,
                    color=COLORS[risk_level],
                    opacity=0.80,
                ),
                text=subset.apply(
                    lambda r: (
                        f"<b>{r['school_name']}</b><br>"
                        f"District: {r['district']}<br>"
                        f"Province: {r['province']}<br>"
                        f"Risk Score: {r['risk_score']:.3f}<br>"
                        f"Attrition: {r['attrition_pct']}%"
                    ), axis=1
                ),
                hovertemplate="%{text}<extra></extra>",
            ))

        center_lat = filtered["latitude"].mean()
        center_lon = filtered["longitude"].mean()

        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=5.2,
            ),
            margin=dict(t=0, b=0, l=0, r=0),
            height=500,
            legend=dict(
                font=dict(family=FONT, size=12),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#CBD5E1",
                borderwidth=1,
                x=0.01, y=0.99,
            ),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.caption(f"Showing {len(filtered)} schools · Marker size reflects risk score")

    divider()

    # ── Province summary table under map ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-label">High-Risk Concentration by Province</div>', unsafe_allow_html=True)
        prov_high = (
            filtered[filtered["risk_level"] == "High"]
            .groupby("province")
            .agg(High_Risk_Schools=("school_id", "count"), Avg_Score=("risk_score", "mean"))
            .reset_index()
            .sort_values("High_Risk_Schools", ascending=False)
            .rename(columns={
                "province":           "Province",
                "High_Risk_Schools":  "High-Risk Schools",
                "Avg_Score":          "Avg Risk Score",
            })
        )
        prov_high["Avg Risk Score"] = prov_high["Avg Risk Score"].round(3)
        st.dataframe(prov_high, use_container_width=True, hide_index=True, height=240)

    with col_b:
        st.markdown('<div class="section-label">Rural vs Urban Risk Breakdown</div>', unsafe_allow_html=True)
        rural_summary = (
            filtered.groupby(["rural", "risk_level"])
            .size()
            .reset_index(name="count")
        )
        rural_summary["Setting"] = rural_summary["rural"].map({True: "Rural", False: "Urban/Peri-urban"})
        fig_grp = px.bar(
            rural_summary,
            x="Setting",
            y="count",
            color="risk_level",
            color_discrete_map=COLORS,
            barmode="group",
            labels={"count": "Schools", "risk_level": "Risk Level"},
        )
        fig_grp.update_layout(
            height=240,
            margin=dict(t=10, b=10, l=0, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(family=FONT, size=11), title=""),
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0", tickfont=dict(family=FONT, size=11), title="Schools"),
            legend=dict(font=dict(family=FONT, size=11), title=""),
        )
        st.plotly_chart(fig_grp, use_container_width=True, config={"displayModeBar": False})

    info_box(
        "<strong>Note on coordinates:</strong> School coordinates are approximated from district centroids "
        "for this prototype. Precise GPS coordinates will be available once EMIS school-level data "
        "is received from the Ministry of Education Permanent Secretary."
    )

    page_footer()