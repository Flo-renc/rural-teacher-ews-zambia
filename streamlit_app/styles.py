import streamlit as st


def inject_styles():
    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');


    /* =====================================================
       ROOT VARIABLES
    ===================================================== */

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

        --red-600: #DC2626;
        --red-100: #FEE2E2;

        --white: #FFFFFF;

        --radius: 8px;

        --shadow-sm:
            0 1px 3px rgba(0,0,0,0.08),
            0 1px 2px rgba(0,0,0,0.04);

        --shadow-md:
            0 4px 12px rgba(0,0,0,0.08),
            0 2px 6px rgba(0,0,0,0.04);
    }



    /* =====================================================
       GLOBAL APP STYLE
    ===================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"] {

        background-color: var(--slate-50) !important;

        font-family:
            'Inter',
            sans-serif !important;

        color: var(--slate-900) !important;
    }


    [data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        height: 3rem !important;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
    }

    #MainMenu {
        display:none !important;
    }

    footer {
        display:none !important;
    }



    /* =====================================================
       SIDEBAR
    ===================================================== */


    [data-testid="stSidebar"] {

        background-color:
            var(--green-900) !important;

        border-right:none !important;
    }


    /*
       Do NOT style every sidebar element.
       It breaks Streamlit widgets.
    */

    [data-testid="stSidebarContent"] {

        padding:
            0.5rem !important;
    }


    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {

        color:
            #C8E6C9 !important;
    }



    /* =====================================================
       SIDEBAR RADIO NAVIGATION
    ===================================================== */


    [data-testid="stSidebar"] [data-testid="stRadio"] {

        padding:
            0.5rem 0;
    }


    [data-testid="stSidebar"] 
    [data-testid="stRadio"] > div {

        gap:
            0.2rem !important;
    }



    /* Remove radio circles */

    [data-testid="stSidebar"]
    [data-testid="stRadio"] input {

        display:none !important;
    }



    [data-testid="stSidebar"]
    [data-testid="stRadio"] label {

        width:100% !important;

        padding:
            0.65rem 1.1rem !important;

        border-radius:
            6px !important;

        font-size:
            0.875rem !important;

        font-weight:
            500 !important;

        cursor:pointer !important;

        transition:
            background 0.15s ease;
    }



    [data-testid="stSidebar"]
    [data-testid="stRadio"] label:hover {

        background:
            rgba(255,255,255,0.08) !important;
    }



    [data-testid="stSidebar"]
    [data-testid="stRadio"]
    label:has(input:checked) {

        background:
            var(--green-700) !important;

        color:
            white !important;

        font-weight:
            600 !important;
    }




    /* =====================================================
       MAIN CONTENT
    ===================================================== */


    .block-container {

        padding:
            2rem 2.5rem 4rem 2.5rem !important;

        max-width:
            1400px !important;
    }



    /* =====================================================
       TYPOGRAPHY
    ===================================================== */


    h1,
    h2,
    h3 {

        font-family:
            'Inter',
            sans-serif !important;

        font-weight:
            700 !important;

        color:
            var(--slate-900) !important;
    }




    /* =====================================================
       KPI CARDS
    ===================================================== */


    .ews-card {

        border-radius:
            var(--radius);

        padding:
            1.5rem;

        box-shadow:
            var(--shadow-sm);

        border:
            1px solid var(--slate-300);

        height:
            100%;
    }



    .ews-card-label {

        font-size:
            0.7rem;

        font-weight:
            600;

        letter-spacing:
            0.08em;

        text-transform:
            uppercase;

        color:
            var(--slate-500);

        margin-bottom:
            0.4rem;
    }



    .ews-card-value {

        font-size:
            2.4rem;

        font-weight:
            700;

        line-height:
            1;

        color:
            var(--slate-900);
    }



    .ews-card-sub {

        font-size:
            0.78rem;

        color:
            var(--slate-500);
    }




    /* =====================================================
       PAGE HEADER
    ===================================================== */


    .page-header {

        margin-bottom:
            2rem;

        padding-bottom:
            1.25rem;

        border-bottom:
            1px solid var(--slate-300);
    }



    .page-header h1 {

        font-size:
            1.6rem !important;
    }



    .page-header p {

        color:
            var(--slate-500);

        font-size:
            0.88rem;
    }




    /* =====================================================
       SECTION LABELS
    ===================================================== */


    .section-label {

        font-size:
            0.72rem;

        font-weight:
            600;

        letter-spacing:
            0.08em;

        text-transform:
            uppercase;

        color:
            var(--slate-500);

        margin-bottom:
            0.5rem;
    }



    .ews-divider {

        height:
            1px;

        background:
            var(--slate-300);

        margin:
            1.75rem 0;
    }





    /* =====================================================
       ALERT BOX
    ===================================================== */


    .ews-alert {

        background:
            var(--red-100);

        border-left:
            4px solid var(--red-600);

        border-radius:
            var(--radius);

        padding:
            1rem 1.25rem;

        margin-bottom:
            1.5rem;

        font-size:
            0.85rem;

        color:
            #7F1D1D;
    }





    /* =====================================================
       INFO BOX
    ===================================================== */


    .ews-info-box {

        background:
            var(--green-50);

        border:
            1px solid var(--green-200);

        border-radius:
            var(--radius);

        padding:
            1rem 1.25rem;

        font-size:
            0.84rem;

        color:
            var(--green-900);
    }




    /* =====================================================
       FOOTER
    ===================================================== */


    .ews-footer {

        font-size:
            0.75rem;

        color:
            var(--slate-500);

        border-top:
            1px solid var(--slate-300);

        padding-top:
            1rem;

        margin-top:
            3rem;

        display:flex;

        justify-content:
            space-between;
    }



    /* =====================================================
       TABLES
    ===================================================== */


    [data-testid="stDataFrame"] table {

        font-size:
            0.83rem !important;
    }



    /* =====================================================
       PLOTLY
    ===================================================== */


    .js-plotly-plot .plotly {

        border-radius:
            var(--radius);
    }


    </style>
    """, unsafe_allow_html=True)