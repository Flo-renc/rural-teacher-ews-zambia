"""
Teacher records endpoints:
  POST /api/v1/records               — create a single record
  GET  /api/v1/records/{school_code} — all records for a school
  GET  /api/v1/records/province-trend/{province} — aggregate trend for a province
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import TeacherRecord, School
from app.schemas.schemas import (
    TeacherRecordCreate, TeacherRecordOut,
    ProvinceTrendOut, ProvinceTrendPoint,
)
from app.core.security import require_role

router = APIRouter(prefix="/api/v1/records", tags=["Teacher Records"])


@router.post(
    "",
    response_model=TeacherRecordOut,
    status_code=201,
    summary="Add a teacher record for a school-year",
    dependencies=[Depends(require_role("data_admin"))],
)
def create_record(payload: TeacherRecordCreate, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == payload.school_code).first()
    if not school:
        raise HTTPException(404, detail=f"School '{payload.school_code}' not found")

    existing = (
        db.query(TeacherRecord)
        .filter(
            TeacherRecord.school_code == payload.school_code,
            TeacherRecord.year        == payload.year,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            409,
            detail=f"Record for school '{payload.school_code}' year {payload.year} already exists. Use PUT to update.",
        )

    record = TeacherRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get(
    "/province-trend/{province}",
    response_model=ProvinceTrendOut,
    summary="Aggregate teacher count trend for a province — powers Teacher Trends page",
)
def province_trend(province: str, db: Session = Depends(get_db)):
    rows = (
        db.query(
            TeacherRecord.year,
            func.sum(TeacherRecord.teacher_count).label("total_teachers"),
            func.avg(TeacherRecord.ptr).label("avg_ptr"),
        )
        .join(School, TeacherRecord.school_code == School.school_code)
        .filter(School.province == province)
        .group_by(TeacherRecord.year)
        .order_by(TeacherRecord.year)
        .all()
    )

    if not rows:
        raise HTTPException(404, detail=f"No records found for province '{province}'")

    return ProvinceTrendOut(
        province=province,
        trend=[
            ProvinceTrendPoint(
                year           = r.year,
                total_teachers = r.total_teachers or 0,
                avg_ptr        = round(r.avg_ptr, 2) if r.avg_ptr else None,
            )
            for r in rows
        ],
    )


@router.get(
    "/{school_code}",
    response_model=List[TeacherRecordOut],
    summary="All teacher records for a school",
)
def get_records(school_code: str, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == school_code).first()
    if not school:
        raise HTTPException(404, detail=f"School '{school_code}' not found")

    records = (
        db.query(TeacherRecord)
        .filter(TeacherRecord.school_code == school_code)
        .order_by(TeacherRecord.year)
        .all()
    )
    return records
