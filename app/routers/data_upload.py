"""
POST /api/v1/upload/bulletin-csv  — bulk upload MoE Bulletin data from CSV.

Expected CSV columns:
  school_code, name, district, province, school_type, is_rural,
  year, teacher_count, qualified_count, ptr, enrolment, attrition_est
"""

import io
import csv
import logging
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import ProvinceData
from app.schemas.schemas import UploadResultOut
from app.core.security import require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/upload", tags=["Upload"])

REQUIRED_COLUMNS = {
    "province",
    "year",
    "teacher_count_primary",
    "student_enrolment_primary",
    "primary_schools",
    "rural_schools",
    "urban_schools",
}

def _int(value):
    try:
        return int(value) if value and str(value).strip() else None
    except:
        return None


def _float(value):
    try:
        return float(value) if value and str(value).strip() else None
    except:
        return None

@router.post(
    "/bulletin-csv",
    response_model=UploadResultOut,
    summary="Bulk upload MoE Bulletin CSV data",
    dependencies=[Depends(require_role("data_admin"))],
)
async def upload_bulletin_csv(
    file: UploadFile = File(
        ...,
        description="CSV file from MoE Education Statistics Bulletin"
    ),
    db: Session = Depends(get_db),
):

    # ---------------------------------------------------------
    # Validate file type
    # ---------------------------------------------------------

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted"
        )


    # ---------------------------------------------------------
    # Read CSV
    # ---------------------------------------------------------

    content = await file.read()

    try:
        text = content.decode("utf-8-sig")

    except UnicodeDecodeError:
        text = content.decode("latin-1")


    reader = csv.DictReader(
        io.StringIO(text)
    )


    if not reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="CSV file has no header row"
        )


    # ---------------------------------------------------------
    # Normalize column names
    # ---------------------------------------------------------

    normalized_columns = {
        col.strip().lower(): col
        for col in reader.fieldnames
    }


    # Required columns

    missing = REQUIRED_COLUMNS - set(normalized_columns.keys())


    if missing:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "CSV missing required columns",
                "missing_columns": sorted(list(missing)),
                "received_columns": list(normalized_columns.keys())
            }
        )


    # ---------------------------------------------------------
    # Upload counters
    # ---------------------------------------------------------

    processed = 0
    inserted = 0
    updated = 0
    skipped = 0
    errors = []


    # ---------------------------------------------------------
    # Process rows
    # ---------------------------------------------------------

    for i, row in enumerate(reader, start=2):

        processed += 1


        try:

            # convert row keys to lowercase

            clean_row = {
                key.lower().strip(): value
                for key, value in row.items()
            }


            province = clean_row["province"].strip()

            year = int(
                clean_row["year"]
            )


            teacher_count = _int(
                clean_row["teacher_count_primary"]
            )


            student_count = _int(
                clean_row["student_enrolment_primary"]
            )


            primary_schools = _int(
                clean_row["primary_schools"]
            )


            rural_schools = _int(
                clean_row["rural_schools"]
            )


            urban_schools = _int(
                clean_row["urban_schools"]
            )


            # -------------------------------------------------
            # Check existing record
            # -------------------------------------------------

            existing = (
                db.query(ProvinceData)
                .filter(
                    ProvinceData.province == province,
                    ProvinceData.year == year
                )
                .first()
            )


            if existing:

                # update existing bulletin record

                existing.teacher_count_primary = teacher_count
                existing.student_enrolment_primary = student_count
                existing.primary_schools = primary_schools
                existing.rural_schools = rural_schools
                existing.urban_schools = urban_schools


                updated += 1


            else:


                record = ProvinceData(

                    province=province,

                    year=year,

                    teacher_count_primary=teacher_count,

                    student_enrolment_primary=student_count,

                    primary_schools=primary_schools,

                    rural_schools=rural_schools,

                    urban_schools=urban_schools

                )


                db.add(record)

                inserted += 1



        except Exception as e:


            errors.append(
                f"Row {i}: {str(e)}"
            )


            skipped += 1

            continue



    # ---------------------------------------------------------
    # Save database changes
    # ---------------------------------------------------------

    try:

        db.commit()


    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database commit failed: {str(e)}"
        )



    logger.info(
        f"""
        Bulletin upload complete:
        processed={processed}
        inserted={inserted}
        updated={updated}
        skipped={skipped}
        """
    )



    return UploadResultOut(

        rows_processed=processed,

        rows_inserted=inserted,

        rows_updated=updated,

        rows_skipped=skipped,

        errors=errors[:50]

    )


"""@router.post(
    "/bulletin-csv",
    response_model=UploadResultOut,
    summary="Bulk upload MoE Bulletin CSV data",
    dependencies=[Depends(require_role("data_admin"))],
)
async def upload_bulletin_csv(
    file: UploadFile = File(..., description="CSV file from MoE Education Statistics Bulletin"),
    db:   Session    = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, detail="Only .csv files are accepted")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")  # strips BOM if present
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    columns = set(reader.fieldnames or [])

    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise HTTPException(
            400,
            detail=f"CSV is missing required columns: {sorted(missing)}"
        )

    processed = 0
    inserted = 0
    skipped = 0
    errors = []

    for i, row in enumerate(reader, start=2):  # start=2 because row 1 is header
        processed += 1

        try:
            province = row["province"].strip()
            year     = int(row["year"])

            existing = (
                db.query(ProvinceData)
                .filter(
                    ProvinceData.province == province,
                    ProvinceData.year     == year,
                )
                .first()
            )

            if existing:
                existing.teacher_count_primary   = _int(row.get("teacher_count_primary"))
                existing.student_enrolment_primary = _int(row.get("student_enrolment_primary"))
                existing.primary_schools         = _int(row.get("primary_schools"))
                existing.rural_schools           = _int(row.get("rural_schools"))
                existing.urban_schools           = _int(row.get("urban_schools"))
                existing.ptr_primary = _float(row.get("ptr_primary"))

                skipped += 1
            else:
                record = ProvinceData(
                    province                     = province,
                    year                         = year,
                    teacher_count_primary        = _int(row.get("teacher_count_primary")),
                    ptr_primary                  = _float(row.get("ptr_primary")),
                    student_enrolment_primary    = _int(row.get("student_enrolment_primary")),
                    primary_schools              = _int(row.get("primary_schools")),
                    rural_schools                = _int(row.get("rural_schools")),
                    urban_schools                = _int(row.get("urban_schools")),
                )
                db.add(record)
                inserted += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
            continue

    db.commit()
    logger.info(
        f"Upload complete processed={processed} inserted={inserted}"
    )


    return UploadResultOut(
        rows_processed=processed,
        rows_inserted=inserted,
        rows_skipped=skipped,
        errors=errors[:50],
    )
"""