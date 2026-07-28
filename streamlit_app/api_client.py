import os
import logging
from typing import Optional

import requests
import streamlit as st


logger = logging.getLogger(__name__)


API_BASE = os.getenv(
    "EWS_API_URL",
    "http://localhost:8000"
)

print(API_BASE)

TIMEOUT = 10




# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def _headers(include_json=True) -> dict:
    """
    Attach JWT token to protected API requests.
    """

    headers = {}

    if include_json:
        headers["Content-Type"] = "application/json"

    token = st.session_state.get("access_token")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


# ============================================================
# GENERIC REQUEST HANDLERS
# ============================================================

def _get(path: str, params: dict = None):
    """
    GET request wrapper with error handling.
    """

    try:
        response = requests.get(
            f"{API_BASE}{path}",
            params=params,
            headers=_headers(),
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()


    except requests.exceptions.ConnectionError:

        st.warning(
            f"Cannot connect to backend at {API_BASE}. "
            "Displaying fallback data.",
            icon="⚠️"
        )

        return None


    except requests.exceptions.HTTPError as e:

        st.error(
            f"API Error {e.response.status_code}: "
            f"{e.response.text}"
        )

        return None


    except Exception as e:

        st.error(
            f"Unexpected API error: {e}"
        )

        return None



def _post(
    path: str,
    json: dict = None,
    files=None
):
    """
    POST request wrapper with error handling.
    Supports both JSON requests and multipart file uploads.
    """

    try:

        # For file uploads, DO NOT set Content-Type manually.
        # requests will create multipart/form-data automatically.
        headers = _headers(
            include_json=(files is None)
        )

        print("POST URL:", f"{API_BASE}{path}")
        print("POST JSON:", json)
        print("POST FILES:", files)

        response = requests.post(
            f"{API_BASE}{path}",
            json=json if files is None else None,
            files=files,
            headers=headers,
            timeout=TIMEOUT
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()

        return response.json()


    except requests.exceptions.ConnectionError:

        st.warning(
            "Backend unavailable.",
            icon="⚠️"
        )

        return None


    except requests.exceptions.HTTPError as e:

        st.error(
            f"API Error {e.response.status_code}: "
            f"{e.response.text}"
        )

        return None


    except Exception as e:

        st.error(
            f"Unexpected API error: {e}"
        )

        return None



# ============================================================
# AUTH
# ============================================================

def login(
    username: str,
    password: str
) -> bool:

    response = requests.post(


        f"{API_BASE}/api/v1/auth/login",
        data={
            "username": username,
            "password": password
        },
        timeout=TIMEOUT
    )

    if response.status_code == 200:

        token_data = response.json()

        st.session_state["access_token"] = (
            token_data["access_token"]
        )

        user = _get("/api/v1/auth/me")

        st.session_state["current_user"] = user

        return True

    else:
        st.error(
            f"Login failed: {response.text}"
        )

    return False
   



def logout():

    st.session_state.pop(
        "access_token",
        None
    )

    st.session_state.pop(
        "current_user",
        None
    )



def get_current_user():

    return st.session_state.get(
        "current_user"
    )



# ============================================================
# HEALTH
# ============================================================

def get_health():

    response = _get(
        "/health"
    )


    if response:
        return response


    return {
        "status": "offline",
        "database": "unknown",
        "active_model": None,
        "lopo_auc": None,
        "real_model": None
    }



# ============================================================
# OVERVIEW PAGE
# ============================================================

def get_national_summary():

    response = _get(
        "/api/v1/predictions/national-summary"
    )


    if response:
        return response


    # fallback
    return {

        "total_provinces": 10,

        "high_risk": 3,

        "not_at_risk": 7,

        "high_risk_pct": 30.0,

        "avg_risk_score": 0.42,

        "prediction_year": 2025,

        "active_model": "xgb_mock",

        "lopo_auc": None
    }



def get_province_summary():

    response = _get(
        "/api/v1/predictions/by-province"
    )


    if response:
        return response


    return [
        {
            "province": "Western",
            "year": 2025,
            "risk_score": 0.82,
            "risk_label": "high_risk",
            "confidence_pct": 82
        },

        {
            "province": "Central",
            "year": 2025,
            "risk_score": 0.30,
            "risk_label": "not_at_risk",
            "confidence_pct": 70
        }
    ]



# ============================================================
# AT-RISK PROVINCES PAGE
# ============================================================

def get_province_predictions(
    risk_label: Optional[str] = None
):

    params = {}

    if risk_label:
        params["risk_label"] = risk_label


    response = _get(
        "/api/v1/predictions",
        params=params
    )


    return response or []



# ============================================================
# MODEL INFERENCE
# ============================================================

def run_prediction(
    province: str,
    year: int
):

    return _post(
        f"/api/v1/predictions/run/{province}",
        json={"year": year}
    )



def run_all_predictions(
    year: int = 2025
):

    return _post(
        "/api/v1/predictions/run-all",
        json={
            "year": year
        }
    )



# ============================================================
# MODEL INSIGHTS (SHAP)
# ============================================================

def get_province_shap(
    province: str
):

    return _get(
        f"/api/v1/predictions/{province}/shap"
    )



# ============================================================
# TEACHER TRENDS
# ============================================================

def get_province_trend(
    province: str
):

    return _get(
        f"/api/v1/predictions/{province}/trend"
    )



# ============================================================
# DATA ADMIN - CSV UPLOAD
# ============================================================

def upload_bulletin(
    file
):

    files = {

        "file": (
            file.name,
            file,
            "text/csv"
        )
    }


    return _post(
        "/api/v1/upload/bulletin-csv",
        files=files
    )



# ============================================================
# MODEL INFORMATION
# ============================================================

def get_active_model_info():

    health = get_health()


    return {

        "model_version":
            health.get(
                "model",
                "xgb_v1.0"
            ),

        "status":
            health.get(
                "status"
            ),

        "database":
            health.get(
                "database"
            )
    }