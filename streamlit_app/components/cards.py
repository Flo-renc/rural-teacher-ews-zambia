import streamlit as st

def metric_card(label, value, sub=None, accent=None):
    """
    accent: None | 'high' | 'medium' | 'low'
    """
    accent_colors = {
        "high":   ("#DC2626", "#FEE2E2"),
        "medium": ("#92400E", "#FEF3C7"),
        "low":    ("#2D6A4F", "#F0FAF4"),
    # Green
    }

    border_color = "#CBD5E1"
    bg_color = "#FFFFFF"

    if accent and accent in accent_colors:
        text_c, bg_color = accent_colors[accent]
        border_color = text_c
    sub_html = f'<div class="ews-card-sub">{sub}</div>' if sub else ""
    st.markdown(f""" div class="ews-card" style="background:{bg_color}; border-color:{border_color};">
        <div class="ews-card-label">{label}</div>
        <div class="ews-card-value">{value}</div>
        {sub_html}
        </div>""", unsafe_allow_html=True)
def section_header(title, description=None):
    desc_html = f'<p>{description}</p>' if description else ""
    st.markdown(f"""
    <div class="page-header">
        <h1>{title}</h1>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)
 
 
def risk_badge(level):
    cls = f"badge-{level.lower()}"
    return f'<span class="badge {cls}">{level}</span>'
 
 
def divider():
    st.markdown('<div class="ews-divider"></div>', unsafe_allow_html=True)
 
 
def info_box(text):
    st.markdown(f'<div class="ews-info-box">{text}</div>', unsafe_allow_html=True)
 
 
def alert_banner(text):
    st.markdown(f'<div class="ews-alert">{text}</div>', unsafe_allow_html=True)
 
 
def page_footer():
    st.markdown("""
    <div class="ews-footer">
        <span>Teacher Attrition EWS &nbsp;&middot;&nbsp; Zambia Ministry of Education</span>
        <span>Data: MoE Education Statistics Bulletin 2022 &nbsp;&middot;&nbsp; Model: XGBoost v1.0</span>
    </div>
    """, unsafe_allow_html=True)
 