"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.connection import get_db
from app.schemas.schemas import HealthResponse
from app.services.ml_service import model_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="API health check")
def health_check(db: Session = Depends(get_db)):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    return HealthResponse(
        status       = "ok" if db_ok else "degraded",
        api_version  = "1.0.0",
        model_loaded = model_service.is_ready(),
        db_connected = db_ok,
    )
