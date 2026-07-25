import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

from api_client import get_province_summary

from components.cards import (
    section_header,
    divider,
    info_box,
    page_footer,
)


# -------------------------------------------------
# GeoJSON configuration
# -------------------------------------------------

GEOJSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "zambia_provinces.geojson"
)


def load_geojson():

    if not os.path.exists(GEOJSON_PATH):
        st.error(
            "GeoJSON file not found. "
            "Place zambia_provinces.geojson inside "
            "streamlit_app/data/"
        )
        st.stop()

    with open(
        GEOJSON_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        geojson = json.load(file)

    if "features" not in geojson:
        st.error("Invalid GeoJSON format.")
        st.stop()

    return geojson



# -------------------------------------------------
# Page
# -------------------------------------------------

def render():

    section_header(
        "Province Risk Map",
        "Geographic distribution of teacher attrition risk across Zambia's 10 provinces"
    )


    # -----------------------------
    # Load prediction data
    # -----------------------------

    provinces = get_province_summary()

    df = pd.DataFrame(provinces)


    if df.empty:
        st.warning(
            "No province prediction data available. "
            "Please run the national risk assessment first."
        )
        return



    # -----------------------------
    # Select year
    # -----------------------------

    years = sorted(
        df["year"].unique(),
        reverse=True
    )


    selected_year = st.selectbox(
        "Select prediction year",
        years,
        key="province_risk_map_year"
    )


    filtered = df[
        df["year"] == selected_year
    ].copy()



    # -----------------------------
    # Clean province names
    # Match GADM GeoJSON
    # -----------------------------

    filtered["province"] = (
        filtered["province"]
        .astype(str)
        .str.strip()
    )


    filtered["province"] = filtered["province"].replace({
        "North-Western": "North Western"
    })



    # -----------------------------
    # Load map
    # -----------------------------

    geojson = load_geojson()



    divider()


    st.markdown(
        '<div class="section-label">'
        'Teacher Attrition Risk by Province'
        '</div>',
        unsafe_allow_html=True
    )



    # -----------------------------
    # Create map
    # -----------------------------

    fig = px.choropleth_mapbox(
        filtered,

        geojson=geojson,

        locations="province",

        featureidkey="properties.NAME_1",

        color="risk_score",

        color_continuous_scale=[
            [0, "#40916C"],
            [0.5, "#F59E0B"],
            [1, "#DC2626"],
        ],

        range_color=(0, 1),

        mapbox_style="carto-positron",

        center={
            "lat": -13.1339,
            "lon": 27.8493
        },

        zoom=4.8,

        opacity=0.8,

        labels={
            "risk_score": "Risk Score"
        },

        hover_data={
            "province": True,
            "risk_score": ":.3f",
            "risk_label": True,
            "confidence_pct": ":.1f",
        }
    )


    fig.update_layout(
        height=550,

        margin=dict(
            t=0,
            b=0,
            l=0,
            r=0
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        coloraxis_colorbar=dict(
            title="Risk Score"
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


    st.caption(
        f"Showing province-level risk scores for {selected_year}. "
        "Red indicates higher predicted teacher attrition risk."
    )



    divider()



    # -----------------------------
    # Ranking table
    # -----------------------------

    st.markdown(
        '<div class="section-label">'
        'Province Risk Ranking'
        '</div>',
        unsafe_allow_html=True
    )


    table_columns = [
        "province",
        "risk_score",
        "risk_label",
        "confidence_pct",
        "ptr_primary_calc",
        "teacher_growth_rate",
        "attrition_proxy_rate",
    ]


    available_columns = [
        col for col in table_columns
        if col in filtered.columns
    ]


    table = filtered[
        available_columns
    ].copy()



    table = table.sort_values(
        "risk_score",
        ascending=False
    )



    rename_map = {
        "province": "Province",
        "risk_score": "Risk Score",
        "risk_label": "Risk Label",
        "confidence_pct": "Confidence %",
        "ptr_primary_calc": "PTR",
        "teacher_growth_rate": "Teacher Growth",
        "attrition_proxy_rate": "Attrition Proxy",
    }


    table = table.rename(
        columns=rename_map
    )


    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        height=350
    )



    # -----------------------------
    # Explanation
    # -----------------------------

    info_box(
        """
        <strong>Map interpretation:</strong><br>
        Provinces shaded red have higher predicted teacher 
        attrition risk according to the XGBoost model.
        Green provinces represent lower predicted risk,
        while intermediate colours indicate moderate risk.
        """
    )


    page_footer()