from app.models.db_models import MLModel
from app.models.db_models import ProvincePrediction
from app.database.connection import SessionLocal

with SessionLocal() as db:
    for model in db.query(MLModel).all():
        print(
            model.model_version,
            model.is_active,
            model.lopo_auc_mean
        )