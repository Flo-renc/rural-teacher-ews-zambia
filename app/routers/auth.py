"""
POST /api/v1/auth/register  — create a new user
POST /api/v1/auth/login     — return JWT
GET  /api/v1/auth/me        — current user profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import User
from app.schemas.schemas import UserCreate, UserOut, TokenOut, LoginRequest
from app.core.security import (
    hash_password, verify_password,
    create_access_token, get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

ALLOWED_ROLES = {"district_officer", "data_admin", "viewer"}


@router.post("/register", response_model=UserOut, status_code=201,
             summary="Register a new user")
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
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut, summary="Login and receive JWT")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut, summary="Get current user profile")
def me(current_user: User = Depends(get_current_user)):
    return current_user
