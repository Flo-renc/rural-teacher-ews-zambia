from datetime import datetime
import json

from app.database.connection import SessionLocal
from app.models.db_models import MLModel


db = SessionLocal()


model = MLModel(
    model_version="xgb_v1.0",
    algorithm="XGBoost",

    # Validation metrics from notebook
    f1_score=0.6310,
    recall_score=None,
    auc_score=0.7679,

    lopo_auc_mean=0.7679,
    lopo_auc_std=0.1693,

    trained_at=datetime.now(),

    artefact_path="app/ml_models/xgb_v1.0.joblib",

    is_active=1,

    feature_cols=json.dumps([
        "ptr_primary_calc",
        "teacher_growth_rate",
        "enrolment_growth_rate",
        "recruitment_gap",
        "teachers_per_school",
        "learners_per_school",
        "rural_school_pct",
        "ptr_trend_3yr"
    ]),

    notes=(
        "XGBoost teacher attrition risk classifier. "
        "Validated using Leave-One-Province-Out cross validation "
        "on Zambia education statistics data."
    )
)


db.add(model)
db.commit()

print("Model registered successfully")

db.close()