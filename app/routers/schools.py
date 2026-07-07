"""
Schools endpoints:
  GET    /api/v1/schools                    — list with filters
  POST   /api/v1/schools                    — create
  GET    /api/v1/schools/{school_code}      — detail
  PUT    /api/v1/schools/{school_code}      — update
  DELETE /api/v1/schools/{school_code}      — delete
  GET    /api/v1/schools/{school_code}/trend — teacher trend for one school
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import School, TeacherRecord
from app.schemas.schemas import (
    SchoolCreate, SchoolUpdate, SchoolOut, SchoolListOut,
    SchoolTrendOut, TeacherTrendPoint,
)
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/api/v1/schools", tags=["Schools"])


@router.get("", response_model=SchoolListOut, summary="List schools with optional filters")
def list_schools(
    province:    Optional[str] = Query(None),
    district:    Optional[str] = Query(None),
    school_type: Optional[str] = Query(None),
    is_rural:    Optional[int] = Query(None),
    skip: int = Query(0,   ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(School)
    if province:    q = q.filter(School.province    == province)
    if district:    q = q.filter(School.district    == district)
    if school_type: q = q.filter(School.school_type == school_type)
    if is_rural is not None: q = q.filter(School.is_rural == is_rural)

    total   = q.count()
    schools = q.order_by(School.province, School.name).offset(skip).limit(limit).all()
    return SchoolListOut(total=total, schools=schools)


@router.post("", response_model=SchoolOut, status_code=201,
             summary="Create a new school record",
             dependencies=[Depends(require_role("data_admin"))])
def create_school(payload: SchoolCreate, db: Session = Depends(get_db)):
    if db.query(School).filter(School.school_code == payload.school_code).first():
        raise HTTPException(409, detail=f"School '{payload.school_code}' already exists")
    school = School(**payload.model_dump())
    db.add(school)
    db.commit()
    db.refresh(school)
    return school


@router.get("/{school_code}", response_model=SchoolOut, summary="Get a single school by code")
def get_school(school_code: str, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == school_code).first()
    if not school:
        raise HTTPException(404, detail=f"School '{school_code}' not found")
    return school


@router.put("/{school_code}", response_model=SchoolOut, summary="Update school details",
            dependencies=[Depends(require_role("data_admin"))])
def update_school(school_code: str, payload: SchoolUpdate, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == school_code).first()
    if not school:
        raise HTTPException(404, detail=f"School '{school_code}' not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(school, field, value)
    db.commit()
    db.refresh(school)
    return school


@router.delete("/{school_code}", status_code=204, summary="Delete a school",
               dependencies=[Depends(require_role("data_admin"))])
def delete_school(school_code: str, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == school_code).first()
    if not school:
        raise HTTPException(404, detail=f"School '{school_code}' not found")
    db.delete(school)
    db.commit()


@router.get("/{school_code}/trend", response_model=SchoolTrendOut,
            summary="Historical teacher trend for a specific school")
def school_trend(school_code: str, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == school_code).first()
    if not school:
        raise HTTPException(404, detail=f"School '{school_code}' not found")

    records = (
        db.query(TeacherRecord)
        .filter(TeacherRecord.school_code == school_code)
        .order_by(TeacherRecord.year)
        .all()
    )
    return SchoolTrendOut(
        school_code = school.school_code,
        school_name = school.name,
        province    = school.province,
        district    = school.district,
        trend       = [
            TeacherTrendPoint(
                year          = r.year,
                teacher_count = r.teacher_count,
                ptr           = r.ptr,
                attrition_est = r.attrition_est,
            )
            for r in records
        ],
    )
