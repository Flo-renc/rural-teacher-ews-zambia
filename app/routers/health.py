from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db
from app.models.db_models import MLModel
from app.schemas.schemas import HealthOut
from app.services.ml_service import ml_service

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthOut)
def health_check(db: Session = Depends(get_db)):

    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    # Registered model check
    active = (
        db.query(MLModel)
        .filter(MLModel.is_active == 1)
        .first()
    )

    ml_service._try_load()

    # Actual ML service check
    try:
        real_model = ml_service.is_real_model
        ml_status = "ok"
    except Exception as e:
        real_model = False
        ml_status = f"ML error: {e}"


    if ml_status != "ok":
        db_status = f"{db_status} | {ml_status}"



    return HealthOut(
        status="ok",
        database=db_status,
        active_model=active.model_version if active else None,
        lopo_auc=active.lopo_auc_mean if active else None,
        real_model=real_model,
    )
