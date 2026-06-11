"""
Predictions router — single prediction, batch prediction, history.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.database.connection import get_db
from app.schemas.schemas import (
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
    SHAPEntry,
)
from app.services.ml_service import model_service
from app.models.db_models import RiskPrediction, RiskLabel, MLModel
from datetime import datetime, timezone

router = APIRouter()


def _save_prediction(db: Session, school_code: str, result: dict):
    """Persist a prediction to the database."""
    pred = RiskPrediction(
        school_code    = school_code,
        model_version  = result["model_version"],
        risk_score     = result["risk_score"],
        risk_label     = RiskLabel(result["risk_label"]),
        shap_json      = json.dumps(result["shap_explanation"]),
        confidence_pct = result["confidence_pct"],
        predicted_at   = result["predicted_at"],
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


def _build_response(school_code: str, result: dict) -> PredictionResponse:
    shap_entries = [SHAPEntry(**e) for e in result["shap_explanation"]]
    return PredictionResponse(
        school_code           = school_code,
        risk_label            = result["risk_label"],
        risk_score            = result["risk_score"],
        confidence_pct        = result["confidence_pct"],
        shap_explanation      = shap_entries,
        model_version         = result["model_version"],
        predicted_at          = result["predicted_at"],
        plain_language_summary= result["plain_language_summary"],
    )


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Single-school attrition risk prediction",
    description=(
        "Submit feature values for one school and receive a binary attrition risk "
        "classification, probability score, SHAP feature attributions, and a "
        "plain-language summary for district officers."
    ),
)
def predict_single(
    request: PredictionRequest,
    db: Session = Depends(get_db),
):
    features = request.model_dump(exclude={"school_code"})
    result = model_service.predict(features)
    _save_prediction(db, request.school_code, result)
    return _build_response(request.school_code, result)


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Batch prediction for multiple schools",
    description=(
        "Submit up to 200 school records at once. Returns ranked predictions "
        "ordered by descending risk score."
    ),
)
def predict_batch(
    request: BatchPredictionRequest,
    db: Session = Depends(get_db),
):
    predictions = []
    for record in request.records:
        features = record.model_dump(exclude={"school_code"})
        result = model_service.predict(features)
        _save_prediction(db, record.school_code, result)
        predictions.append(_build_response(record.school_code, result))

    # Sort by risk score descending
    predictions.sort(key=lambda p: p.risk_score, reverse=True)
    high_risk_count = sum(1 for p in predictions if p.risk_label == "high_risk")

    return BatchPredictionResponse(
        total           = len(predictions),
        high_risk_count = high_risk_count,
        predictions     = predictions,
        model_version   = model_service.is_ready() and predictions[0].model_version or "not_loaded",
    )


@router.get(
    "/predict/history/{school_code}",
    response_model=list[PredictionResponse],
    summary="Prediction history for a school",
    description="Returns all past predictions for the given school code, newest first.",
)
def prediction_history(
    school_code: str,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    records = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.school_code == school_code)
        .order_by(RiskPrediction.predicted_at.desc())
        .limit(limit)
        .all()
    )
    results = []
    for rec in records:
        shap_raw = json.loads(rec.shap_json) if rec.shap_json else []
        shap_entries = [SHAPEntry(**e) for e in shap_raw]
        results.append(PredictionResponse(
            school_code            = rec.school_code,
            risk_label             = rec.risk_label.value,
            risk_score             = rec.risk_score,
            confidence_pct         = rec.confidence_pct or round(rec.risk_score * 100, 1),
            shap_explanation       = shap_entries,
            model_version          = rec.model_version,
            predicted_at           = rec.predicted_at,
            plain_language_summary = "",
        ))
    return results
