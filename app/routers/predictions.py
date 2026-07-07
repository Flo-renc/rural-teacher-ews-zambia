"""
Predictions endpoints:
  POST /api/v1/predictions/run/{school_code}   — run ML inference for one school
  POST /api/v1/predictions/run-all             — run inference for all schools
  GET  /api/v1/predictions/                    — latest prediction per school
  GET  /api/v1/predictions/national-summary    — KPI counts for Overview page
  GET  /api/v1/predictions/by-province         — per-province risk breakdown
  GET  /api/v1/predictions/{school_code}/shap  — SHAP values for one school
  GET  /api/v1/predictions/{school_code}/latest — latest prediction for one school
"""

import json
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import School, TeacherRecord, RiskPrediction, MLModel
from app.schemas.schemas import (
    PredictionCreate, PredictionOut,
    RiskSummaryItem, NationalSummaryOut, ProvinceSummaryItem,
)
from app.core.security import require_role
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


def _get_active_model(db: Session) -> MLModel:
    model = db.query(MLModel).filter(MLModel.is_active == 1).first()
    if not model:
        raise HTTPException(404, detail="No active ML model found. Seed ml_models table first.")
    return model


def _latest_per_school(db: Session):
    """Subquery: latest predicted_at per school_code."""
    return (
        db.query(
            RiskPrediction.school_code,
            func.max(RiskPrediction.predicted_at).label("max_date"),
        )
        .group_by(RiskPrediction.school_code)
        .subquery()
    )


# ── Run inference ─────────────────────────────────────────────────────────────

@router.post(
    "/run/{school_code}",
    response_model=PredictionOut,
    status_code=201,
    summary="Run ML inference for a single school",
    dependencies=[Depends(require_role("data_admin", "district_officer"))],
)
def run_prediction(school_code: str, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == school_code).first()
    if not school:
        raise HTTPException(404, detail=f"School '{school_code}' not found")

    # Get latest teacher record for this school
    record = (
        db.query(TeacherRecord)
        .filter(TeacherRecord.school_code == school_code)
        .order_by(TeacherRecord.year.desc())
        .first()
    )
    if not record:
        raise HTTPException(422, detail=f"No teacher records found for school '{school_code}'")

    active_model = _get_active_model(db)

    features = {
        "teacher_count":   record.teacher_count,
        "qualified_count": record.qualified_count,
        "ptr":             record.ptr,
        "enrolment":       record.enrolment,
        "attrition_est":   record.attrition_est,
        "is_rural":        school.is_rural,
    }

    result = ml_service.predict(features)

    prediction = RiskPrediction(
        school_code    = school_code,
        model_version  = active_model.model_version,
        risk_score     = result["risk_score"],
        risk_label     = result["risk_label"],
        shap_json      = result["shap_json"],
        confidence_pct = result["confidence_pct"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


@router.post(
    "/run-all",
    summary="Run inference for every school with teacher records",
    dependencies=[Depends(require_role("data_admin"))],
)
def run_all_predictions(db: Session = Depends(get_db)):
    active_model = _get_active_model(db)
    schools      = db.query(School).all()
    inserted = skipped = 0
    errors   = []

    for school in schools:
        record = (
            db.query(TeacherRecord)
            .filter(TeacherRecord.school_code == school.school_code)
            .order_by(TeacherRecord.year.desc())
            .first()
        )
        if not record:
            skipped += 1
            continue
        try:
            features = {
                "teacher_count":   record.teacher_count,
                "qualified_count": record.qualified_count,
                "ptr":             record.ptr,
                "enrolment":       record.enrolment,
                "attrition_est":   record.attrition_est,
                "is_rural":        school.is_rural,
            }
            result     = ml_service.predict(features)
            prediction = RiskPrediction(
                school_code    = school.school_code,
                model_version  = active_model.model_version,
                risk_score     = result["risk_score"],
                risk_label     = result["risk_label"],
                shap_json      = result["shap_json"],
                confidence_pct = result["confidence_pct"],
            )
            db.add(prediction)
            inserted += 1
        except Exception as e:
            errors.append(f"{school.school_code}: {e}")

    db.commit()
    return {"inserted": inserted, "skipped": skipped, "errors": errors}


# ── Read predictions ──────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=List[RiskSummaryItem],
    summary="Latest prediction per school — powers At-Risk Schools table",
)
def list_predictions(
    province:   Optional[str] = Query(None),
    district:   Optional[str] = Query(None),
    risk_label: Optional[str] = Query(None, regex="^(high_risk|not_at_risk)$"),
    is_rural:   Optional[int] = Query(None),
    skip:  int = Query(0,   ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    latest_sub = _latest_per_school(db)

    q = (
        db.query(RiskPrediction, School)
        .join(School, RiskPrediction.school_code == School.school_code)
        .join(
            latest_sub,
            (RiskPrediction.school_code  == latest_sub.c.school_code) &
            (RiskPrediction.predicted_at == latest_sub.c.max_date),
        )
    )
    if province:   q = q.filter(School.province   == province)
    if district:   q = q.filter(School.district   == district)
    if risk_label: q = q.filter(RiskPrediction.risk_label == risk_label)
    if is_rural is not None: q = q.filter(School.is_rural == is_rural)

    rows = q.order_by(RiskPrediction.risk_score.desc()).offset(skip).limit(limit).all()

    return [
        RiskSummaryItem(
            school_code    = pred.school_code,
            school_name    = school.name,
            province       = school.province,
            district       = school.district,
            school_type    = school.school_type,
            is_rural       = school.is_rural,
            risk_score     = pred.risk_score,
            risk_label     = pred.risk_label,
            confidence_pct = pred.confidence_pct,
            predicted_at   = pred.predicted_at,
        )
        for pred, school in rows
    ]


@router.get(
    "/national-summary",
    response_model=NationalSummaryOut,
    summary="KPI counts — powers the Overview page banner",
)
def national_summary(db: Session = Depends(get_db)):
    latest_sub = _latest_per_school(db)

    rows = (
        db.query(RiskPrediction)
        .join(
            latest_sub,
            (RiskPrediction.school_code  == latest_sub.c.school_code) &
            (RiskPrediction.predicted_at == latest_sub.c.max_date),
        )
        .all()
    )

    if not rows:
        return NationalSummaryOut(
            total_schools=0, high_risk=0, not_at_risk=0,
            high_risk_pct=0.0, avg_risk_score=0.0,
            provinces_flagged=0, active_model=None,
        )

    total     = len(rows)
    high_risk = sum(1 for r in rows if r.risk_label == "high_risk")
    avg_score = round(sum(r.risk_score for r in rows) / total, 4)

    # Count distinct provinces flagged high risk
    high_codes = {r.school_code for r in rows if r.risk_label == "high_risk"}
    provinces_flagged = (
        db.query(School.province)
        .filter(School.school_code.in_(high_codes))
        .distinct()
        .count()
    )

    active_model = (
        db.query(MLModel.model_version).filter(MLModel.is_active == 1).scalar()
    )

    return NationalSummaryOut(
        total_schools     = total,
        high_risk         = high_risk,
        not_at_risk       = total - high_risk,
        high_risk_pct     = round(high_risk / total * 100, 1),
        avg_risk_score    = avg_score,
        provinces_flagged = provinces_flagged,
        active_model      = active_model,
    )


@router.get(
    "/by-province",
    response_model=List[ProvinceSummaryItem],
    summary="Per-province risk breakdown — powers Overview province table",
)
def by_province(db: Session = Depends(get_db)):
    latest_sub = _latest_per_school(db)

    rows = (
        db.query(RiskPrediction, School)
        .join(School, RiskPrediction.school_code == School.school_code)
        .join(
            latest_sub,
            (RiskPrediction.school_code  == latest_sub.c.school_code) &
            (RiskPrediction.predicted_at == latest_sub.c.max_date),
        )
        .all()
    )

    province_map: dict = {}
    for pred, school in rows:
        p = school.province
        if p not in province_map:
            province_map[p] = {"total": 0, "high": 0, "not": 0, "scores": []}
        province_map[p]["total"] += 1
        province_map[p]["scores"].append(pred.risk_score)
        if pred.risk_label == "high_risk":
            province_map[p]["high"] += 1
        else:
            province_map[p]["not"] += 1

    return [
        ProvinceSummaryItem(
            province  = prov,
            total     = data["total"],
            high_risk = data["high"],
            not_at_risk = data["not"],
            avg_score = round(sum(data["scores"]) / len(data["scores"]), 4),
        )
        for prov, data in sorted(province_map.items())
    ]


@router.get(
    "/{school_code}/latest",
    response_model=PredictionOut,
    summary="Latest prediction for a specific school",
)
def latest_prediction(school_code: str, db: Session = Depends(get_db)):
    prediction = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.school_code == school_code)
        .order_by(RiskPrediction.predicted_at.desc())
        .first()
    )
    if not prediction:
        raise HTTPException(404, detail=f"No predictions found for school '{school_code}'")
    return prediction


@router.get(
    "/{school_code}/shap",
    summary="SHAP feature explanation for a school's latest prediction",
)
def school_shap(school_code: str, db: Session = Depends(get_db)):
    prediction = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.school_code == school_code)
        .order_by(RiskPrediction.predicted_at.desc())
        .first()
    )
    if not prediction:
        raise HTTPException(404, detail=f"No predictions found for school '{school_code}'")
    if not prediction.shap_json:
        raise HTTPException(404, detail="No SHAP data stored for this prediction")

    return {
        "school_code":  school_code,
        "risk_score":   prediction.risk_score,
        "risk_label":   prediction.risk_label,
        "predicted_at": prediction.predicted_at,
        "shap_values":  json.loads(prediction.shap_json),
    }
