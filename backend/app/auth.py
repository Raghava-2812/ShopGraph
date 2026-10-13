"""
ShopGraph - Authentication & Security Utilities
app/auth.py

This module provides security functions and FastAPI dependency injection helpers:
  - Secure password hashing and verification using bcrypt (via passlib).
  - JSON Web Token (JWT) issuance, signing, and expiration handling (via python-jose).
  - Current user authentication dependency (`get_current_user` for protected endpoints).
  - Optional user authentication dependency (`get_optional_user` for personalized endpoints
    that also allow guest access).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.sqlite_db import get_sqlite_db, User

# Password hashing context configured with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 bearer token scheme pointing to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Generate a secure cryptographic salted hash of a plaintext password.

    Args:
        password (str): Plaintext password to hash.

    Returns:
        str: Bcrypt salted password hash.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify whether a candidate plaintext password matches the stored bcrypt hash.

    Args:
        plain (str): Candidate plaintext password entered by user.
        hashed (str): Stored bcrypt password hash.

    Returns:
        bool: True if password matches; False otherwise.
    """
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token containing arbitrary payload claims and expiration.

    Args:
        data (dict): Claims dictionary to encode (typically {"sub": user_id}).
        expires_delta (timedelta | None): Custom expiration delta. Defaults to settings.JWT_EXPIRE_MINUTES.

    Returns:
        str: Encoded and signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a signed JWT token signature and expiration.

    Args:
        token (str): JWT string received in Authorization header.

    Returns:
        dict: Decoded payload claims dictionary.

    Raises:
        HTTPException: 401 Unauthorized if token is malformed, expired, or invalid.
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_sqlite_db),
) -> User:
    """FastAPI dependency: require and return the currently authenticated user from Bearer token.

    Args:
        token (str): Bearer token extracted from HTTP Authorization header.
        db (Session): SQLAlchemy database session.

    Returns:
        User: Authenticated User ORM model from SQLite database.

    Raises:
        HTTPException: 401 Unauthorized if token is missing, invalid, or user does not exist.
    """
    payload = decode_token(token)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_optional_user(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)),
    db: Session = Depends(get_sqlite_db),
) -> Optional[User]:
    """FastAPI dependency: return current User if valid Bearer token provided, otherwise None.

    Enables endpoints (such as `/recommendations` and `/products/{name}`) to deliver
    personalized recommendations for authenticated customers while gracefully serving
    guest visitors without raising authentication errors.

    Args:
        token (str | None): Optional Bearer token from request headers.
        db (Session): SQLAlchemy database session.

    Returns:
        User | None: User entity if token is valid, or None for guests.
    """
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return db.query(User).filter(User.id == int(user_id)).first()
    except Exception:
        return None

