"""
Authentication API endpoints.

This module provides endpoints for:

- User registration.
- User authentication using JWT.
- Retrieving the currently authenticated user.

These endpoints support role-based access control for the
Teacher Attrition Early Warning System.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import User
from app.schemas.schemas import UserCreate, UserOut, TokenOut
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
ALLOWED_ROLES = {"district_officer", "data_admin", "viewer"}

# Authentication Endpoints

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if payload.role not in ALLOWED_ROLES:
        raise HTTPException(400, detail=f"Role must be one of: {ALLOWED_ROLES}")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(409, detail="Username already exists")
    user = User(
        username      = payload.username,
        password_hash = hash_password(payload.password),
        role          = payload.role,
        province      = payload.province,
    )
    db.add(user); db.commit(); db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )

    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )

    return TokenOut(
        access_token=token
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

