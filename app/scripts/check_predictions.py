from sqlalchemy import func
from app.models.db_models import ProvincePrediction
from app.database.connection import SessionLocal


with SessionLocal() as db:

    rows = (
        db.query(
            ProvincePrediction.province,
            ProvincePrediction.year,
            ProvincePrediction.model_version,
        )
        .limit(50)
        .all()
    )

    print("Prediction rows:")
    for row in rows:
        print(row)

    latest = (
        db.query(func.max(ProvincePrediction.year))
        .scalar()
    )

    print("\nLatest prediction year:", latest)