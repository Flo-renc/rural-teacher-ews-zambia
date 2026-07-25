"""
Authentication and authorization utilities.

This module provides functionality for:

- Password hashing and verification using bcrypt.
- JWT access token creation and validation.
- Retrieving the authenticated user from a JWT.
- Role-based authorization dependencies for FastAPI endpoints.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import User

# Authentication and Configuration

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Password Utilities

def hash_password(plain: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        plain: User's plaintext password.

    Returns:
        The hashed password.
    """
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain: User's plaintext password.
        hashed: The hashed password to compare against.

    Returns:
        True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain, hashed)

# JWT Token Utilities

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Payload to encode into the token.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT access token.
    """
    to_encode = data.copy()
    expire    = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT access token.

    Returns:
        Decoded payload.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication Dependencies

def get_current_user(
    token: str   = Depends(oauth2_scheme),
    db:   Session = Depends(get_db),
) -> User:
    """
    Retrieve the currently authenticated user.

    Args:
        token: JWT access token.
        db: Database session.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException: If the token is invalid or the user
            cannot be found.
    """
    payload  = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles: str):
    """
    Create a dependency that restricts endpoint access to
    specific user roles.

    Args:
        *roles: One or more permitted roles.

    Returns:
        FastAPI dependency function.
    """
    def _check(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{current_user.role}' is not permitted."
            )
        return current_user
    return _check