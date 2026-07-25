"""
Province data endpoints — bulletin raw data.

GET  /api/v1/provinces/                      → list all province-year records
GET  /api/v1/provinces/{province}/trend      → historical teacher counts
POST /api/v1/provinces/                      → add one record
POST /api/v1/provinces/upload-csv            → bulk CSV upload
"""
import io, csv
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import ProvinceData
from app.schemas.schemas import ProvinceDataCreate, ProvinceDataOut, UploadResultOut
from app.core.security import require_role

router = APIRouter(prefix="/api/v1/provinces", tags=["Province Data"])

PROVINCES = [
    "Central","Copperbelt","Eastern","Luapula","Lusaka",
    "Muchinga","North-Western","Northern","Southern","Western",
]


@router.get("", response_model=List[ProvinceDataOut],
            summary="List province bulletin data")
def list_data(
    province: Optional[str] = Query(None),
    year:     Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(ProvinceData)
    if province: q = q.filter(ProvinceData.province == province)
    if year:     q = q.filter(ProvinceData.year     == year)
    return q.order_by(ProvinceData.province, ProvinceData.year).all()


@router.post("", response_model=ProvinceDataOut, status_code=201,
             dependencies=[Depends(require_role("data_admin"))])
def create_record(payload: ProvinceDataCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(ProvinceData)
        .filter(ProvinceData.province == payload.province,
                ProvinceData.year     == payload.year)
        .first()
    )
    if existing:
        raise HTTPException(409, f"{payload.province} {payload.year} already exists. Use PUT to update.")
    row = ProvinceData(**payload.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return row


@router.get("/{province}/trend", summary="Historical teacher data for one province")
def province_trend(province: str, db: Session = Depends(get_db)):
    rows = (
        db.query(ProvinceData)
        .filter(ProvinceData.province == province)
        .order_by(ProvinceData.year)
        .all()
    )
    if not rows:
        raise HTTPException(404, f"No data for province '{province}'")
    return [
        {
            "year":                      r.year,
            "teacher_count_primary":     r.teacher_count_primary,
            "student_enrolment_primary": r.student_enrolment_primary,
            "primary_schools":           r.primary_schools,
            "rural_schools":             r.rural_schools,
            "urban_schools":             r.urban_schools,
        }
        for r in rows
    ]


@router.post(
    "/upload-csv",
    response_model=UploadResultOut,
    summary="Bulk upload bulletin CSV",
    dependencies=[Depends(require_role("data_admin"))],
)
async def upload_csv(
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only .csv files accepted")

    content = await file.read()
    text    = content.decode("utf-8-sig")
    reader  = csv.DictReader(io.StringIO(text))

    REQUIRED = {"province", "year", "teacher_count_primary", "student_enrolment_primary"}
    missing  = REQUIRED - set(reader.fieldnames or [])
    if missing:
        raise HTTPException(400, f"CSV missing columns: {sorted(missing)}")

    processed = inserted = skipped = 0
    errors    = []

    for i, row in enumerate(reader, 2):
        processed += 1
        province = row.get("province","").strip()
        if not province:
            errors.append(f"Row {i}: missing province"); skipped += 1; continue
        try:
            year = int(row["year"])
        except:
            errors.append(f"Row {i}: invalid year"); skipped += 1; continue

        existing = (
            db.query(ProvinceData)
            .filter(ProvinceData.province == province, ProvinceData.year == year)
            .first()
        )
        if existing:
            skipped += 1; continue

        def _int(v):
            try: return int(v) if v and str(v).strip() else None
            except: return None
        def _float(v):
            try: return float(v) if v and str(v).strip() else None
            except: return None

        try:
            db.add(ProvinceData(
                province                  = province,
                year                      = year,
                teacher_count_primary     = _int(row.get("teacher_count_primary")),
                student_enrolment_primary = _int(row.get("student_enrolment_primary")),
                ptr_primary_bulletin      = _float(row.get("ptr_primary")),
                primary_schools           = _int(row.get("Primary_Schools")),
                rural_schools             = _int(row.get("Rural_schools")),
                urban_schools             = _int(row.get("Urban_schools")),
            ))
            inserted += 1
        except Exception as e:
            errors.append(f"Row {i}: {e}"); skipped += 1
            db.rollback(); continue

    db.commit()
    return UploadResultOut(
        rows_processed = processed,
        rows_inserted  = inserted,
        rows_skipped   = skipped,
        errors         = errors[:50],
    )