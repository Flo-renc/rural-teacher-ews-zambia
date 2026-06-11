"""
Schools router — CRUD for school records.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.schemas import SchoolCreate, SchoolResponse
from app.models.db_models import School

router = APIRouter()


@router.get(
    "/schools",
    response_model=list[SchoolResponse],
    summary="List all schools",
)
def list_schools(
    province : str | None = None,
    district : str | None = None,
    is_rural : bool | None = None,
    limit    : int = 100,
    db       : Session = Depends(get_db),
):
    q = db.query(School)
    if province:
        q = q.filter(School.province == province)
    if district:
        q = q.filter(School.district == district)
    if is_rural is not None:
        q = q.filter(School.is_rural == is_rural)
    return q.limit(limit).all()


@router.get(
    "/schools/{school_code}",
    response_model=SchoolResponse,
    summary="Get a single school by code",
)
def get_school(school_code: str, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == school_code).first()
    if not school:
        raise HTTPException(status_code=404, detail=f"School '{school_code}' not found.")
    return school


@router.post(
    "/schools",
    response_model=SchoolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new school",
)
def create_school(school: SchoolCreate, db: Session = Depends(get_db)):
    existing = db.query(School).filter(School.school_code == school.school_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="School code already exists.")
    db_school = School(**school.model_dump())
    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    return db_school


@router.delete(
    "/schools/{school_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a school record",
)
def delete_school(school_code: str, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.school_code == school_code).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found.")
    db.delete(school)
    db.commit()