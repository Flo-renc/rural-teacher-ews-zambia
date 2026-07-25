"""
Province prediction endpoints — powers every dashboard page.

GET  /api/v1/predictions/national-summary    → Overview KPIs
GET  /api/v1/predictions/                    → At-Risk Provinces table
GET  /api/v1/predictions/by-province         → province list with risk scores
GET  /api/v1/predictions/{province}/shap     → SHAP for Model Insights
GET  /api/v1/predictions/{province}/trend    → risk trend for Teacher Trends
POST /api/v1/predictions/run/{province}      → run inference for one province
POST /api/v1/predictions/run-all             → run inference for all provinces
"""
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import ProvinceData, ProvincePrediction, MLModel
from app.schemas.schemas import (
    PredictionOut, NationalSummaryOut, ProvinceSummaryItem, SHAPOut,
)
from app.core.security import require_role
from app.services.ml_service import ml_service, build_feature_vector

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])

PROVINCES = [
    "Central","Copperbelt","Eastern","Luapula","Lusaka",
    "Muchinga","North-Western","Northern","Southern","Western",
]


def _get_active_model(db: Session) -> MLModel:
    m = db.query(MLModel).filter(MLModel.is_active == 1).first()
    if not m:
        raise HTTPException(404, "No active model found. Seed ml_models table first.")
    return m


def _latest_prediction_year(db: Session) -> int:
    """Return the most recent year that has predictions."""
    result = db.query(func.max(ProvincePrediction.year)).scalar()
    return result or 2025


# ── Run inference ─────────────────────────────────────────────

@router.post(
    "/run/{province}",
    response_model=PredictionOut,
    status_code=201,
    summary="Run ML inference for one province",
    dependencies=[Depends(require_role("data_admin", "district_officer"))],
)
def run_prediction(province: str, year: int = Query(2025), db: Session = Depends(get_db)):
    # Fetch current year record
    record = (
        db.query(ProvinceData)
        .filter(ProvinceData.province == province, ProvinceData.year == year)
        .first()
    )
    if not record:
        raise HTTPException(404, f"No data for {province} year {year}")

    # Fetch prior year (for growth rates)
    prior_years = (
        db.query(ProvinceData)
        .filter(ProvinceData.province == province, ProvinceData.year < year)
        .order_by(ProvinceData.year.desc())
        .limit(2)
        .all()
    )
    prior         = prior_years[0].__dict__ if len(prior_years) > 0 else None
    two_years_ago = prior_years[1].__dict__ if len(prior_years) > 1 else None

    features = build_feature_vector(record.__dict__, prior, two_years_ago)
    result   = ml_service.predict(features)
    model    = _get_active_model(db)

    # Compute attrition proxy
    tc_prev  = prior.get("teacher_count_primary", 1) if prior else 1
    tc_curr  = record.teacher_count_primary or 1
    net_loss = max(0, tc_prev - tc_curr)
    atr_rate = round(net_loss / tc_prev, 4)

    pred = ProvincePrediction(
        province             = province,
        year                 = year,
        model_version        = model.model_version,
        risk_score           = result["risk_score"],
        risk_label           = result["risk_label"],
        confidence_pct       = result["confidence_pct"],
        ptr_primary_calc     = features.get("ptr_primary_calc"),
        teacher_growth_rate  = features.get("teacher_growth_rate"),
        recruitment_gap      = features.get("recruitment_gap"),
        rural_school_pct     = features.get("rural_school_pct"),
        attrition_proxy_rate = atr_rate,
        shap_json            = result["shap_json"],
    )
    # Upsert — update if already exists
    existing = (
        db.query(ProvincePrediction)
        .filter(
            ProvincePrediction.province      == province,
            ProvincePrediction.year          == year,
            ProvincePrediction.model_version == model.model_version,
        )
        .first()
    )
    if existing:
        for k, v in pred.__dict__.items():
            if not k.startswith("_"):
                setattr(existing, k, v)
        db.commit(); db.refresh(existing)
        return existing

    db.add(pred); db.commit(); db.refresh(pred)
    return pred


@router.post(
    "/run-all",
    summary="Run inference for all provinces",
    dependencies=[Depends(require_role("data_admin"))],
)
def run_all(year: int = Query(2025), db: Session = Depends(get_db)):
    inserted = skipped = 0
    errors   = []
    for province in PROVINCES:
        try:
            run_prediction.__wrapped__ if hasattr(run_prediction, "__wrapped__") else None
            # Call directly to reuse logic
            record = (
                db.query(ProvinceData)
                .filter(ProvinceData.province == province, ProvinceData.year == year)
                .first()
            )
            if not record:
                skipped += 1
                errors.append(f"{province}: no data for {year}")
                continue

            prior_years = (
                db.query(ProvinceData)
                .filter(ProvinceData.province == province, ProvinceData.year < year)
                .order_by(ProvinceData.year.desc())
                .limit(2).all()
            )
            prior         = prior_years[0].__dict__ if len(prior_years) > 0 else None
            two_years_ago = prior_years[1].__dict__ if len(prior_years) > 1 else None

            features = build_feature_vector(record.__dict__, prior, two_years_ago)
            result   = ml_service.predict(features)
            model    = _get_active_model(db)

            tc_prev  = prior.get("teacher_count_primary", 1) if prior else 1
            tc_curr  = record.teacher_count_primary or 1
            atr_rate = round(max(0, tc_prev - tc_curr) / tc_prev, 4)

            existing = (
                db.query(ProvincePrediction)
                .filter(
                    ProvincePrediction.province      == province,
                    ProvincePrediction.year          == year,
                    ProvincePrediction.model_version == model.model_version,
                ).first()
            )
            row_data = dict(
                province             = province,
                year                 = year,
                model_version        = model.model_version,
                risk_score           = result["risk_score"],
                risk_label           = result["risk_label"],
                confidence_pct       = result["confidence_pct"],
                ptr_primary_calc     = features.get("ptr_primary_calc"),
                teacher_growth_rate  = features.get("teacher_growth_rate"),
                recruitment_gap      = features.get("recruitment_gap"),
                rural_school_pct     = features.get("rural_school_pct"),
                attrition_proxy_rate = atr_rate,
                shap_json            = result["shap_json"],
            )
            if existing:
                for k, v in row_data.items():
                    setattr(existing, k, v)
            else:
                db.add(ProvincePrediction(**row_data))
            inserted += 1
        except Exception as e:
            errors.append(f"{province}: {e}")
            skipped += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped, "errors": errors}


# ── Read predictions ──────────────────────────────────────────

@router.get("", response_model=List[ProvinceSummaryItem],
            summary="All province predictions — At-Risk Provinces table")
def list_predictions(
    year:       Optional[int] = Query(None),
    risk_label: Optional[str] = Query(None, regex="^(high_risk|not_at_risk)$"),
    db: Session = Depends(get_db),
):
    
    q  = db.query(ProvincePrediction)
    if year:
        q = q.filter(ProvincePrediction.year == year)
    if risk_label:
        q = q.filter(ProvincePrediction.risk_label == risk_label)
    rows = q.order_by(ProvincePrediction.risk_score.desc()).all()
    return rows


@router.get(
    "/national-summary",
    response_model=NationalSummaryOut,
    summary="KPI counts — Overview page banner",
)
def national_summary(year: Optional[int] = Query(None), db: Session = Depends(get_db)):
    yr   = year or _latest_prediction_year(db)
    rows = db.query(ProvincePrediction).filter(ProvincePrediction.year == yr).all()

    if not rows:
        return NationalSummaryOut(
            total_provinces=0, high_risk=0, not_at_risk=0,
            high_risk_pct=0.0, avg_risk_score=0.0,
            prediction_year=yr, active_model=None, lopo_auc=None,
        )

    total     = len(rows)
    high_risk = sum(1 for r in rows if r.risk_label == "high_risk")
    avg_score = round(sum(r.risk_score for r in rows) / total, 4)
    active    = db.query(MLModel).filter(MLModel.is_active == 1).first()

    return NationalSummaryOut(
        total_provinces = total,
        high_risk       = high_risk,
        not_at_risk     = total - high_risk,
        high_risk_pct   = round(high_risk / total * 100, 1),
        avg_risk_score  = avg_score,
        prediction_year = yr,
        active_model    = active.model_version if active else None,
        lopo_auc        = active.lopo_auc_mean if active else None,
    )


@router.get(
    "/by-province",
    response_model=List[ProvinceSummaryItem],
    summary="Province list sorted by risk — Overview province table",
)
def by_province(year: Optional[int] = Query(None), db: Session = Depends(get_db)):
    yr = year or _latest_prediction_year(db)
    return (
        db.query(ProvincePrediction)
        .filter(ProvincePrediction.year == yr)
        .order_by(ProvincePrediction.risk_score.desc())
        .all()
    )


@router.get(
    "/{province}/shap",
    response_model=SHAPOut,
    summary="SHAP explanation — Model Insights page",
)
def province_shap(province: str, year: Optional[int] = Query(None),
                  db: Session = Depends(get_db)):
    yr   = year or _latest_prediction_year(db)
    pred = (
        db.query(ProvincePrediction)
        .filter(ProvincePrediction.province == province,
                ProvincePrediction.year     == yr)
        .first()
    )
    if not pred:
        raise HTTPException(404, f"No prediction for {province} year {yr}")
    if not pred.shap_json:
        raise HTTPException(404, f"No SHAP data stored for {province} year {yr}")

    return SHAPOut(
        province     = province,
        year         = yr,
        risk_score   = pred.risk_score,
        risk_label   = pred.risk_label,
        predicted_at = pred.predicted_at,
        shap_values  = json.loads(pred.shap_json),
    )


@router.get(
    "/{province}/trend",
    summary="Historical risk scores for one province — Teacher Trends page",
)
def province_trend(province: str, db: Session = Depends(get_db)):
    rows = (
        db.query(ProvincePrediction)
        .filter(ProvincePrediction.province == province)
        .order_by(ProvincePrediction.year)
        .all()
    )
    return [
        {
            "year":                 r.year,
            "risk_score":           r.risk_score,
            "risk_label":           r.risk_label,
            "ptr_primary_calc":     r.ptr_primary_calc,
            "teacher_growth_rate":  r.teacher_growth_rate,
            "recruitment_gap":      r.recruitment_gap,
            "attrition_proxy_rate": r.attrition_proxy_rate,
        }
        for r in rows
    ]