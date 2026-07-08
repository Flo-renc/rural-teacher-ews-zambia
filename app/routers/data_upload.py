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
from app.models.db_models import School, TeacherRecord
from app.schemas.schemas import UploadResultOut
from app.core.security import require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/upload", tags=["Upload"])

REQUIRED_COLUMNS = {
    "school_code", "name", "district", "province",
    "year", "teacher_count",
}


@router.post(
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

    rows_processed = rows_inserted = rows_skipped = 0
    errors = []

    for i, row in enumerate(reader, start=2):  # start=2 because row 1 is header
        rows_processed += 1
        school_code = row.get("school_code", "").strip()
        if not school_code:
            errors.append(f"Row {i}: missing school_code — skipped")
            rows_skipped += 1
            continue

        try:
            # Upsert school
            school = db.query(School).filter(School.school_code == school_code).first()
            if not school:
                school = School(
                    school_code = school_code,
                    name        = row.get("name", "").strip() or school_code,
                    district    = row.get("district", "").strip(),
                    province    = row.get("province", "").strip(),
                    school_type = row.get("school_type", "").strip() or None,
                    is_rural    = int(row.get("is_rural", 1) or 1),
                )
                db.add(school)
                db.flush()

            # Parse year
            year = int(row["year"])

            # Skip if record already exists
            exists = (
                db.query(TeacherRecord)
                .filter(
                    TeacherRecord.school_code == school_code,
                    TeacherRecord.year        == year,
                )
                .first()
            )
            if exists:
                rows_skipped += 1
                continue

            def _int(val):
                try: return int(val) if val and str(val).strip() else None
                except: return None

            def _float(val):
                try: return float(val) if val and str(val).strip() else None
                except: return None

            record = TeacherRecord(
                school_code     = school_code,
                year            = year,
                teacher_count   = _int(row.get("teacher_count")),
                qualified_count = _int(row.get("qualified_count")),
                ptr             = _float(row.get("ptr")),
                enrolment       = _int(row.get("enrolment")),
                attrition_est   = _int(row.get("attrition_est")),
            )
            db.add(record)
            rows_inserted += 1

        except Exception as e:
            errors.append(f"Row {i} ({school_code}): {e}")
            rows_skipped += 1
            db.rollback()
            continue

    db.commit()
    logger.info(
        f"CSV upload complete — processed:{rows_processed}, "
        f"inserted:{rows_inserted}, skipped:{rows_skipped}, errors:{len(errors)}"
    )
    return UploadResultOut(
        rows_processed = rows_processed,
        rows_inserted  = rows_inserted,
        rows_skipped   = rows_skipped,
        errors         = errors[:50],  # cap error list to 50
    )
