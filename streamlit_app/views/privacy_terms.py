"""
Privacy Policy & Terms of Use

This page explains how data are handled within the
Rural Teacher Attrition Early Warning System (EWS).
"""

import streamlit as st

from components.cards import (
    section_header,
    info_box,
    divider,
    page_footer,
)


def render():

    section_header(
        "Privacy Policy & Terms of Use",
        "Data governance, acceptable use, and system responsibilities."
    )

    info_box("""
    <strong>Research Prototype</strong><br><br>

    This application is a research prototype developed as part of an
    African Leadership University Software Engineering Capstone Project.

    It is intended to support early identification of teacher attrition
    risk using aggregate Ministry of Education statistics. The system
    provides decision support only and must not be used as the sole basis
    for policy or employment decisions.
    """)

    divider()

    st.subheader("Purpose of the System")

    st.write("""
The Rural Teacher Attrition Early Warning System (EWS) predicts teacher
attrition risk at the provincial level using publicly available
administrative education statistics.

Its purpose is to assist Ministry of Education officials in identifying
provinces that may require additional investigation or intervention.
Predictions are probabilistic estimates and should always be interpreted
alongside professional judgement.
""")

    divider()

    st.subheader("Data Collected")

    st.write("""
The system does **not** collect or store personal information about
teachers or learners.

The application processes only aggregate education statistics,
including:

- Province
- Year
- Teacher counts
- Learner enrolment
- Number of schools
- Rural and urban school counts
- Model-generated risk scores
- SHAP explainability values
- Prediction timestamps

For authentication purposes, the application stores only:

- Username
- User role
- Assigned province (where applicable)

Passwords are securely hashed and are never stored in plain text.
""")

    divider()

    st.subheader("Data Ownership")

    st.write("""
All education statistics remain the property of the
**Ministry of Education, Republic of Zambia**.

The machine learning predictions, visualisations, and SHAP explanations
are generated solely for this research prototype and do not replace
official Ministry records.
""")

    divider()

    st.subheader("Data Retention")

    st.write("""
Uploaded Ministry datasets remain in the application's database until
they are replaced by a newer upload or removed by a Data Administrator.

Prediction records are retained for reproducibility, auditing,
and comparison of model performance.

No personal teacher or learner records are retained.
""")

    divider()

    st.subheader("Access Control")

    st.write("""
Access to the system is controlled through secure authentication and
role-based authorization.

The following roles are supported:
""")

    st.table({
        "Role": [
            "Viewer",
            "Provincial Officer",
            "Data Administrator"
        ],
        "Permissions": [
            "View dashboard and predictions",
            "View provincial predictions",
            "Upload datasets, run predictions, manage the system"
        ]
    })

    divider()

    st.subheader("Appropriate Use")

    st.write("""
Users should understand that:

- Predictions indicate probability rather than certainty.
- Results should support planning and investigation.
- Predictions should never be interpreted as evidence of failure.
- Human expertise should always be used when making decisions.
""")

    divider()

    st.subheader("Explainable Artificial Intelligence")

    st.write("""
Each prediction includes a SHAP explanation that identifies the factors
which contributed most to the predicted risk score.

This improves transparency by allowing users to understand why a
province has been classified as higher or lower risk rather than relying
on a black-box prediction.
""")

    divider()

    st.subheader("Disclaimer")

    st.warning("""
This application is a research prototype developed for academic
purposes.

It has not been certified for operational deployment within the
Ministry of Education and should not be used as the sole basis for
resource allocation or policy decisions.
""")

    page_footer()