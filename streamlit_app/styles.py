import streamlit as st


def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

    /* ── Root tokens ── */
    :root {
        --green-900: #1B4332;
        --green-700: #2D6A4F;
        --green-500: #40916C;
        --green-200: #B7E4C7;
        --green-50:  #F0FAF4;
        --slate-900: #0F172A;
        --slate-700: #334155;
        --slate-500: #64748B;
        --slate-300: #CBD5E1;
        --slate-100: #F1F5F9;
        --slate-50:  #F8FAFC;
        --amber-500: #F59E0B;
        --amber-100: #FEF3C7;
        --red-600:   #DC2626;
        --red-100:   #FEE2E2;
        --white:     #FFFFFF;
        --radius:    8px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);
    }

    /* ── Base resets ── */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--slate-50) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--slate-900) !important;
    }

    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: var(--green-900) !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] * {
        color: #E2F0E8 !important;
    }
    [data-testid="stSidebarContent"] {
        padding: 0 !important;
    }

    /* ── Main content padding ── */
    .block-container {
        padding: 2rem 2.5rem 4rem 2.5rem !important;
        max-width: 1400px !important;
    }

    /* ── Typography ── */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: var(--slate-900) !important;
        letter-spacing: -0.02em !important;
    }

    /* ── Cards ── */
    .ews-card {
        background: var(--white);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--slate-300);
        height: 100%;
    }

    .ews-card-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--slate-500);
        margin-bottom: 0.4rem;
    }

    .ews-card-value {
        font-size: 2.4rem;
        font-weight: 700;
        line-height: 1;
        color: var(--slate-900);
        margin-bottom: 0.25rem;
    }

    .ews-card-sub {
        font-size: 0.78rem;
        color: var(--slate-500);
    }

    /* ── Risk badges ── */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-high   { background: var(--red-100);   color: var(--red-600); }
    .badge-medium { background: var(--amber-100);  color: #92400E; }
    .badge-low    { background: var(--green-50);   color: var(--green-700); }

    /* ── Page header ── */
    .page-header {
        margin-bottom: 2rem;
        padding-bottom: 1.25rem;
        border-bottom: 1px solid var(--slate-300);
    }
    .page-header h1 {
        font-size: 1.6rem !important;
        margin-bottom: 0.25rem !important;
    }
    .page-header p {
        color: var(--slate-500);
        font-size: 0.88rem;
        margin: 0;
    }

    /* ── Section label above charts ── */
    .section-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--slate-500);
        margin-bottom: 0.5rem;
    }

    /* ── Divider ── */
    .ews-divider {
        height: 1px;
        background: var(--slate-300);
        margin: 1.75rem 0;
    }

    /* ── Alert banner ── */
    .ews-alert {
        background: var(--red-100);
        border-left: 4px solid var(--red-600);
        border-radius: var(--radius);
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
        font-size: 0.85rem;
        color: #7F1D1D;
    }
    .ews-alert strong { color: var(--red-600); }

    /* ── Metric delta override ── */
    [data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

    /* ── Dataframe table ── */
    [data-testid="stDataFrame"] table {
        font-size: 0.83rem !important;
    }

    /* ── Sidebar nav item ── */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.65rem 1.25rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 500;
        transition: background 0.15s;
        margin: 0.15rem 0.75rem;
        color: #C8E6C9;
        text-decoration: none;
    }
    .nav-item:hover   { background: rgba(255,255,255,0.08); color: #fff; }
    .nav-item.active  { background: var(--green-700); color: #fff; font-weight: 600; }

    /* ── Streamlit radio / button overrides for sidebar ── */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 0.1rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 0.6rem 1.1rem !important;
        border-radius: 6px !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: #C8E6C9 !important;
        cursor: pointer;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: var(--green-700) !important;
        color: #fff !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,0.08) !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {
        border-radius: var(--radius) !important;
        border-color: var(--slate-300) !important;
        font-size: 0.875rem !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] [role="tab"] {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--green-700) !important;
        border-bottom-color: var(--green-700) !important;
    }

    /* ── Plotly chart backgrounds ── */
    .js-plotly-plot .plotly { border-radius: var(--radius); }

    /* ── Info box ── */
    .ews-info-box {
        background: var(--green-50);
        border: 1px solid var(--green-200);
        border-radius: var(--radius);
        padding: 1rem 1.25rem;
        font-size: 0.84rem;
        color: var(--green-900);
    }
    .ews-info-box strong { color: var(--green-700); }

    /* ── Footer strip ── */
    .ews-footer {
        font-size: 0.75rem;
        color: var(--slate-500);
        border-top: 1px solid var(--slate-300);
        padding-top: 1rem;
        margin-top: 3rem;
        display: flex;
        justify-content: space-between;
    }

    </style>
    """, unsafe_allow_html=True)