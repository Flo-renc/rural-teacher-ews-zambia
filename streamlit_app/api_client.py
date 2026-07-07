import os
import logging
from typing import Optional
import requests
import streamlit as st

logger = logging.getLogger(__name__)

API_BASE = os.getenv("EWS_API_URL", "http://localhost:8000")
TIMEOUT = 10  # seconds

# ── Auth token helpers ────────────────────────────────────────────────────────

def _headers() -> dict:
    """"Include JWT token if one is stored in session state"""
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def _get(path: str, params: dict = None):
    """GET with error handling. Returns parsed JSON or None."""
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, headers=_headers(), timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.warning(
            f"Cannot reach the API at **{API_BASE}**. "
            "Showing mock data. Start the backend with `uvicorn app.main:app --reload`.",
            icon="⚠️",
        )
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def _post(path: str, json: dict = None, files=None, data=None):
    """POST with error handling. Returns parsed JSON or None."""
    try:
        r = requests.post(
            f"{API_BASE}{path}",
            json=json,
            files=files,
            data=data,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.warning(f"Cannot reach the API at **{API_BASE}**.", icon="⚠️")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════

def login(username: str, password: str) -> bool:
    """Authenticate and store JWT in session state. Returns True on success."""
    result = _post("/api/v1/auth/login", json={"username": username, "password": password})
    if result and "access_token" in result:
        st.session_state["access_token"] = result["access_token"]
        me = _get("/api/v1/auth/me")
        if me:
            st.session_state["current_user"] = me
        return True
    return False


def logout():
    st.session_state.pop("access_token",    None)
    st.session_state.pop("current_user",    None)


def get_current_user() -> Optional[dict]:
    return st.session_state.get("current_user")


# ══════════════════════════════════════════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════════════════════════════════════════

def get_health() -> dict:
    result = _get("/api/v1/health")
    if result:
        return result
    return {"status": "unknown", "database": "unreachable", "model": None}


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW / NATIONAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def get_national_summary() -> dict:
    result = _get("/api/v1/predictions/national-summary")
    if result:
        return result
    # Mock fallback
    return {
        "total_schools":     120,
        "high_risk":         32,
        "not_at_risk":       88,
        "high_risk_pct":     26.7,
        "avg_risk_score":    0.41,
        "provinces_flagged": 6,
        "active_model":      "xgb_v1.0 (mock)",
    }


def get_province_summary() -> list:
    result = _get("/api/v1/predictions/by-province")
    if result:
        return result
    # Mock fallback
    from data import generate_schools
    import pandas as pd
    df = generate_schools(120)
    rows = []
    for prov, grp in df.groupby("province"):
        rows.append({
            "province":    prov,
            "total":       len(grp),
            "high_risk":   (grp["risk_level"] == "High").sum(),
            "not_at_risk": (grp["risk_level"] != "High").sum(),
            "avg_score":   round(grp["risk_score"].mean(), 4),
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# SCHOOLS
# ══════════════════════════════════════════════════════════════════════════════

def get_schools(
    province:    Optional[str] = None,
    district:    Optional[str] = None,
    school_type: Optional[str] = None,
    is_rural:    Optional[int] = None,
    limit: int = 500,
) -> dict:
    params = {"limit": limit}
    if province:    params["province"]    = province
    if district:    params["district"]    = district
    if school_type: params["school_type"] = school_type
    if is_rural is not None: params["is_rural"] = is_rural

    result = _get("/api/v1/schools", params=params)
    if result:
        return result
    # Mock fallback
    from data import generate_schools
    df = generate_schools(120)
    return {"total": len(df), "schools": df.to_dict("records")}


# ══════════════════════════════════════════════════════════════════════════════
# PREDICTIONS / RISK TABLE
# ══════════════════════════════════════════════════════════════════════════════

def get_predictions(
    province:   Optional[str] = None,
    district:   Optional[str] = None,
    risk_label: Optional[str] = None,
    is_rural:   Optional[int] = None,
    limit: int = 500,
) -> list:
    params = {"limit": limit}
    if province:   params["province"]   = province
    if district:   params["district"]   = district
    if risk_label: params["risk_label"] = risk_label
    if is_rural is not None: params["is_rural"] = is_rural

    result = _get("/api/v1/predictions", params=params)
    if result is not None:
        return result
    # Mock fallback
    from data import generate_schools
    df = generate_schools(120)
    df["risk_label"] = df["risk_level"].map({"High": "high_risk", "Medium": "not_at_risk", "Low": "not_at_risk"})
    df["school_name"] = df["school_name"]
    return df.to_dict("records")


def get_school_shap(school_code: str) -> Optional[dict]:
    return _get(f"/api/v1/predictions/{school_code}/shap")


def run_prediction(school_code: str) -> Optional[dict]:
    return _post(f"/api/v1/predictions/run/{school_code}")


# ══════════════════════════════════════════════════════════════════════════════
# TEACHER RECORDS / TRENDS
# ══════════════════════════════════════════════════════════════════════════════

def get_province_trend(province: str) -> Optional[dict]:
    return _get(f"/api/v1/records/province-trend/{province}")


def get_school_trend(school_code: str) -> Optional[dict]:
    return _get(f"/api/v1/schools/{school_code}/trend")


# ══════════════════════════════════════════════════════════════════════════════
# ML MODEL INFO
# ══════════════════════════════════════════════════════════════════════════════

def get_active_model_info() -> dict:
    health = get_health()
    return {
        "model_version": health.get("model") or "xgb_v1.0",
        "status":        health.get("status"),
        "database":      health.get("database"),
    }
