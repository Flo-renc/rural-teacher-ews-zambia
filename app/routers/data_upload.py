"""
Data upload router — accepts a CSV matching the MoE Bulletin format,
computes features, runs batch prediction, and persists results.
"""

import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.schemas import UploadResponse
from app.services.ml_service import model_service, FEATURE_COLS
from app.models.db_models import School, TeacherRecord, RiskPrediction, RiskLabel
from datetime import datetime, timezone
import json

router = APIRouter()

REQUIRED_COLS = {
    "school_code", "province", "district", "level", "year",
    "teachers", "teachers_prev", "ptr", "enrolment",
    "enrolment_prev", "qualified_ratio", "attrition_est",
    "schools_rural", "schools_urban",
}


def _compute_features(row: pd.Series) -> dict:
    """
    Reproduce the feature engineering from the notebook for a single row.
    All national-level reference values are taken from the MoE Bulletin 2022.
    """
    NATIONAL_PTR_MEAN = 35.1
    NATIONAL_PTR_STD  = 9.6

    teachers_prev = max(row.get("teachers_prev", row["teachers"] * 0.95), 1)
    enrolment_prev = max(row.get("enrolment_prev", row["enrolment"] * 0.95), 1)
    total_schools = max(row.get("schools_rural", 1) + row.get("schools_urban", 1), 1)

    teacher_delta = (row["teachers"] - teachers_prev) / teachers_prev * 100
    enrolment_growth = (row["enrolment"] - enrolment_prev) / enrolment_prev * 100

    return {
        "ptr_deviation":     round((row["ptr"] - NATIONAL_PTR_MEAN) / NATIONAL_PTR_STD, 4),
        "qualification_gap": round(1 - row.get("qualified_ratio", 0.8), 4),
        "rural_isolation":   round(row.get("schools_rural", 0) / total_schools, 4),
        "teacher_delta_pct": round(teacher_delta, 2),
        "enrolment_growth":  round(enrolment_growth, 2),
        "pressure_gap":      round(enrolment_growth - teacher_delta, 2),
        "attrition_rate":    round(row.get("attrition_est", 0) / max(row["teachers"], 1) * 100, 4),
        "is_secondary":      1 if str(row.get("level", "primary")).lower() == "secondary" else 0,
    }


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload MoE Bulletin CSV and refresh predictions",
    description=(
        "Upload a CSV file with school-level teacher data. "
        "The API computes features, runs predictions for all rows, "
        "and persists results to the database. "
        "Required columns: school_code, province, district, level, year, "
        "teachers, teachers_prev, ptr, enrolment, enrolment_prev, "
        "qualified_ratio, attrition_est, schools_rural, schools_urban."
    ),
)
async def upload_bulletin_csv(
    file: UploadFile = File(..., description="CSV file — MoE Bulletin format"),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV is missing required columns: {sorted(missing)}"
        )

    # Clean numeric columns
    numeric_cols = ["teachers", "teachers_prev", "ptr", "enrolment",
                    "enrolment_prev", "qualified_ratio", "attrition_est",
                    "schools_rural", "schools_urban"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["school_code", "teachers", "ptr", "enrolment"])
    df["teachers_prev"]  = df["teachers_prev"].fillna(df["teachers"] * 0.95)
    df["enrolment_prev"] = df["enrolment_prev"].fillna(df["enrolment"] * 0.95)
    df["attrition_est"]  = df["attrition_est"].fillna(0)
    df["qualified_ratio"] = df["qualified_ratio"].fillna(0.80)

    high_risk_count = 0
    rows_processed = 0
    model_version = model_service.is_ready() and "xgb_v1.0" or "model_not_loaded"

    for _, row in df.iterrows():
        features = _compute_features(row)
        result = model_service.predict(features)

        pred = RiskPrediction(
            school_code   = str(row["school_code"]),
            model_version = result["model_version"],
            risk_score    = result["risk_score"],
            risk_label    = RiskLabel(result["risk_label"]),
            shap_json     = json.dumps(result["shap_explanation"]),
            confidence_pct= result["confidence_pct"],
            predicted_at  = datetime.now(timezone.utc),
        )
        db.add(pred)

        if result["risk_label"] == "high_risk":
            high_risk_count += 1
        rows_processed += 1

    db.commit()

    return UploadResponse(
        message         = f"Successfully processed {rows_processed} records.",
        rows_processed  = rows_processed,
        high_risk_count = high_risk_count,
        model_version   = model_version,
    )
