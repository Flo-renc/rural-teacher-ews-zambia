"""
tests/test_api.py

Pytest test suite for the FastAPI backend.
Uses httpx TestClient — no running server needed.

Run with:
    pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ── Sample valid prediction payload ──────────────────────────
VALID_PREDICTION = {
    "school_code":       "TEST_001",
    "ptr_deviation":     0.45,
    "qualification_gap": 0.22,
    "rural_isolation":   0.74,
    "teacher_delta_pct": -18.5,
    "enrolment_growth":  4.2,
    "pressure_gap":      5.8,
    "attrition_rate":    7.2,
    "is_secondary":      0,
}

VALID_SCHOOL = {
    "school_code": "TEST_001",
    "name":        "Chongwe Basic School",
    "district":    "Chongwe",
    "province":    "Lusaka",
    "school_type": "GRZ",
    "is_rural":    True,
}


# ── Health check ──────────────────────────────────────────────

def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "db_connected" in data
    assert "api_version" in data


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "Teacher Attrition EWS API"


# ── Prediction endpoint ───────────────────────────────────────

def test_predict_returns_200():
    r = client.post("/api/v1/predict", json=VALID_PREDICTION)
    assert r.status_code == 200


def test_predict_response_structure():
    r = client.post("/api/v1/predict", json=VALID_PREDICTION)
    data = r.json()
    assert "risk_label"             in data
    assert "risk_score"             in data
    assert "confidence_pct"         in data
    assert "shap_explanation"       in data
    assert "model_version"          in data
    assert "plain_language_summary" in data


def test_predict_risk_score_in_range():
    r = client.post("/api/v1/predict", json=VALID_PREDICTION)
    score = r.json()["risk_score"]
    assert 0.0 <= score <= 1.0


def test_predict_risk_label_valid():
    r = client.post("/api/v1/predict", json=VALID_PREDICTION)
    label = r.json()["risk_label"]
    assert label in ("high_risk", "not_at_risk")


def test_predict_rejects_invalid_qualified_ratio():
    bad = {**VALID_PREDICTION, "qualification_gap": 1.5}  # > 1.0
    r = client.post("/api/v1/predict", json=bad)
    assert r.status_code == 422


def test_predict_rejects_missing_field():
    bad = {k: v for k, v in VALID_PREDICTION.items() if k != "ptr_deviation"}
    r = client.post("/api/v1/predict", json=bad)
    assert r.status_code == 422


# ── Batch prediction endpoint ─────────────────────────────────

def test_batch_predict():
    payload = {"records": [VALID_PREDICTION, {**VALID_PREDICTION, "school_code": "TEST_002"}]}
    r = client.post("/api/v1/predict/batch", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert "high_risk_count" in data
    assert len(data["predictions"]) == 2


def test_batch_sorted_by_risk_score():
    records = [
        {**VALID_PREDICTION, "school_code": "A", "teacher_delta_pct": -25.0},
        {**VALID_PREDICTION, "school_code": "B", "teacher_delta_pct": 5.0},
    ]
    r = client.post("/api/v1/predict/batch", json={"records": records})
    preds = r.json()["predictions"]
    scores = [p["risk_score"] for p in preds]
    assert scores == sorted(scores, reverse=True)


def test_batch_rejects_empty():
    r = client.post("/api/v1/predict/batch", json={"records": []})
    assert r.status_code == 422


# ── Schools endpoint ──────────────────────────────────────────

def test_list_schools():
    r = client.get("/api/v1/schools")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_and_get_school():
    # Create
    r = client.post("/api/v1/schools", json=VALID_SCHOOL)
    assert r.status_code in (201, 409)  # 409 if already exists from previous run

    # Get
    r2 = client.get(f"/api/v1/schools/{VALID_SCHOOL['school_code']}")
    assert r2.status_code == 200
    assert r2.json()["district"] == "Chongwe"


def test_get_nonexistent_school():
    r = client.get("/api/v1/schools/DOES_NOT_EXIST_XYZ")
    assert r.status_code == 404


# ── Upload endpoint ───────────────────────────────────────────

def test_upload_rejects_non_csv():
    r = client.post(
        "/api/v1/upload",
        files={"file": ("test.txt", b"not a csv", "text/plain")},
    )
    assert r.status_code == 400


def test_upload_rejects_missing_columns():
    csv_content = b"school_code,province\nTEST,Lusaka\n"
    r = client.post(
        "/api/v1/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
    )
    assert r.status_code == 422


def test_upload_valid_csv():
    csv_content = (
        "school_code,province,district,level,year,"
        "teachers,teachers_prev,ptr,enrolment,enrolment_prev,"
        "qualified_ratio,attrition_est,schools_rural,schools_urban\n"
        "CHO_001,Lusaka,Chongwe,primary,2022,"
        "18,22,32.5,585,555,0.78,3,399,511\n"
    ).encode()
    r = client.post(
        "/api/v1/upload",
        files={"file": ("bulletin.csv", csv_content, "text/csv")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["rows_processed"] == 1
