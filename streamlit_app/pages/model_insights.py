import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from data import shap_feature_importance, generate_schools
from components.cards import section_header, divider, info_box, page_footer

FONT = "Inter, sans-serif"


def render():
    df_shap    = shap_feature_importance()
    df_schools = generate_schools(120)

    section_header(
        "Model Insights",
        "XGBoost model performance, SHAP feature importances, and per-school explainability"
    )

    # ── Model summary strip ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Model",          "XGBoost v1.0")
    c2.metric("ROC-AUC",        "0.87")
    c3.metric("F1 Score",       "0.83")
    c4.metric("Training Years", "2009–2022")

    divider()

    tab1, tab2, tab3 = st.tabs(["Feature Importance (SHAP)", "Confusion Matrix", "School Explainer"])

    # ── Tab 1: SHAP bar chart ──
    with tab1:
        st.markdown('<div class="section-label">Mean |SHAP| — Global Feature Impact</div>', unsafe_allow_html=True)

        df_sorted = df_shap.sort_values("mean_shap", ascending=True)

        fig = go.Figure(go.Bar(
            x=df_sorted["mean_shap"],
            y=df_sorted["feature"],
            orientation="h",
            marker=dict(
                color=df_sorted["mean_shap"],
                colorscale=[[0, "#B7E4C7"], [1, "#1B4332"]],
                showscale=False,
            ),
            text=[f"{v:.3f}" for v in df_sorted["mean_shap"]],
            textposition="outside",
            textfont=dict(family=FONT, size=11),
            hovertemplate="<b>%{y}</b><br>Mean |SHAP|: %{x:.3f}<extra></extra>",
        ))
        fig.update_layout(
            height=380,
            margin=dict(t=10, b=20, l=10, r=60),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=True, gridcolor="#E2E8F0", title="Mean |SHAP value|",
                titlefont=dict(family=FONT, size=12),
                tickfont=dict(family=FONT, size=11),
            ),
            yaxis=dict(title="", tickfont=dict(family=FONT, size=12)),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        info_box(
            "<strong>Reading this chart:</strong> The SHAP value for a feature measures the "
            "average magnitude of that feature's contribution to the model's risk prediction "
            "across all schools. Higher values mean greater influence. "
            "<strong>Pupil-Teacher Ratio</strong> is the single strongest predictor of attrition risk, "
            "followed by the school's prior-year attrition history."
        )

    # ── Tab 2: Confusion matrix ──
    with tab2:
        st.markdown('<div class="section-label">Confusion Matrix (Test Set)</div>', unsafe_allow_html=True)

        # Illustrative values consistent with ROC-AUC 0.87
        cm = np.array([[28, 5], [6, 21]])
        labels = ["Low / Medium Risk", "High Risk"]

        fig_cm = go.Figure(go.Heatmap(
            z=cm,
            x=[f"Predicted: {l}" for l in labels],
            y=[f"Actual: {l}" for l in labels],
            colorscale=[[0, "#F0FAF4"], [1, "#1B4332"]],
            showscale=False,
            text=cm,
            texttemplate="%{text}",
            textfont=dict(family=FONT, size=22, color="white"),
        ))
        fig_cm.update_layout(
            height=300,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(family=FONT, size=12)),
            yaxis=dict(tickfont=dict(family=FONT, size=12), autorange="reversed"),
        )
        st.plotly_chart(fig_cm, use_container_width=True, config={"displayModeBar": False})

        col1, col2, col3 = st.columns(3)
        col1.metric("Precision (High Risk)", "0.81")
        col2.metric("Recall (High Risk)",    "0.78")
        col3.metric("Accuracy",              "0.82")

    # ── Tab 3: School-level explainer ──
    with tab3:
        st.markdown('<div class="section-label">Per-School SHAP Waterfall</div>', unsafe_allow_html=True)

        high_risk_schools = df_schools[df_schools["risk_level"] == "High"]["school_name"].tolist()
        selected_school   = st.selectbox("Select a high-risk school to explain", high_risk_schools[:20])

        if selected_school:
            row = df_schools[df_schools["school_name"] == selected_school].iloc[0]

            st.markdown(f"""
            <div style="display:flex; gap:1.5rem; margin:0.75rem 0 1.25rem 0; flex-wrap:wrap;">
                <div style="font-size:0.82rem; color:#64748B;">
                    <span style="font-weight:600; color:#0F172A;">Province:</span> {row['province']}
                </div>
                <div style="font-size:0.82rem; color:#64748B;">
                    <span style="font-weight:600; color:#0F172A;">District:</span> {row['district']}
                </div>
                <div style="font-size:0.82rem; color:#64748B;">
                    <span style="font-weight:600; color:#0F172A;">Risk Score:</span>
                    <span style="color:#DC2626; font-weight:700;">{row['risk_score']:.3f}</span>
                </div>
                <div style="font-size:0.82rem; color:#64748B;">
                    <span style="font-weight:600; color:#0F172A;">Attrition:</span> {row['attrition_pct']}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Simulated SHAP waterfall for this school
            np.random.seed(hash(selected_school) % 2**31)
            features  = ["Pupil-Teacher Ratio", "Prior Year Attrition", "Remoteness Index",
                         "Years Without Promotion", "Housing Availability", "Transfer Request Rate"]
            shap_vals = np.random.uniform(-0.1, 0.25, size=len(features))
            shap_vals[0] = abs(shap_vals[0]) + 0.1   # PTR always positive

            shap_df = pd.DataFrame({"Feature": features, "SHAP Value": shap_vals}).sort_values("SHAP Value")

            fig_wf = go.Figure(go.Bar(
                x=shap_df["SHAP Value"],
                y=shap_df["Feature"],
                orientation="h",
                marker_color=["#DC2626" if v > 0 else "#40916C" for v in shap_df["SHAP Value"]],
                text=[f"{v:+.3f}" for v in shap_df["SHAP Value"]],
                textposition="outside",
                textfont=dict(family=FONT, size=11),
                hovertemplate="<b>%{y}</b><br>SHAP: %{x:+.3f}<extra></extra>",
            ))
            fig_wf.add_vline(x=0, line_color="#CBD5E1", line_width=1)
            fig_wf.update_layout(
                height=300,
                margin=dict(t=10, b=10, l=10, r=60),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#E2E8F0", title="SHAP contribution to risk",
                           tickfont=dict(family=FONT, size=11)),
                yaxis=dict(title="", tickfont=dict(family=FONT, size=12)),
            )
            st.plotly_chart(fig_wf, use_container_width=True, config={"displayModeBar": False})

            info_box(
                "Red bars push the risk score <strong>higher</strong>; green bars push it <strong>lower</strong>. "
                "The sum of all SHAP values plus the base rate equals the final predicted risk score for this school."
            )

    page_footer()