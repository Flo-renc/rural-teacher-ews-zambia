import pandas as pd

from app.database.connection import SessionLocal
from app.models.db_models import ProvinceData


CSV_PATH = "data/raw/bulletin_data_statistics.csv"


def load_data():

    db = SessionLocal()

    df = pd.read_csv(CSV_PATH)

    # Avoid duplicate inserts
    existing = db.query(ProvinceData).count()

    if existing > 0:
        print(f"ProvinceData already contains {existing} rows")
        db.close()
        return

    records = []

    for _, row in df.iterrows():

        record = ProvinceData(
            province=row["Province"],
            year=int(row["Year"]),

            teacher_count_primary=int(
                row["Teacher_count_primary"]
            ) if pd.notna(row["Teacher_count_primary"]) else None,

            student_enrolment_primary=int(
                row["Student_enrolment_primary"]
            ) if pd.notna(row["Student_enrolment_primary"]) else None,

            ptr_primary_bulletin=float(
                row["PTR_primary"]
            ) if pd.notna(row["PTR_primary"]) else None,

            primary_schools=int(
                row["Primary_Schools"]
            ) if pd.notna(row["Primary_Schools"]) else None,

            rural_schools=int(
                row["Rural_schools"]
            ) if pd.notna(row["Rural_schools"]) else None,

            urban_schools=int(
                row["Urban_schools"]
            ) if pd.notna(row["Urban_schools"]) else None,
        )

        records.append(record)


    db.bulk_save_objects(records)
    db.commit()

    print(f"Loaded {len(records)} ProvinceData rows")

    db.close()


if __name__ == "__main__":
    load_data()