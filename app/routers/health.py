"""
GET /api/v1/health  — liveness + DB + model status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.connection import get_db
from app.models.db_models import MLModel
from app.schemas.schemas import HealthOut
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


@router.get("", response_model=HealthOut, summary="Service health check")
def health_check(db: Session = Depends(get_db)):
    # DB check
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    # Active model
    active_model = (
        db.query(MLModel.model_version)
        .filter(MLModel.is_active == 1)
        .scalar()
    )

    return HealthOut(
        status="ok",
        database=db_status,
        model=active_model,
    )
