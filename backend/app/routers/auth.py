"""
ShopGraph - User Authentication Router
app/routers/auth.py

This module handles identity and access management for the ShopGraph platform:
  - POST /auth/register: Customer account creation with bcrypt password hashing.
  - POST /auth/login: Credential validation and JWT access token issuance.
  - GET  /auth/me: Profile retrieval for the currently authenticated bearer token.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.sqlite_db import get_sqlite_db, User
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Request / Response Schemas ────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Payload schema for user registration."""
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    """Payload schema for user authentication."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Bearer token authentication response containing token and user profile."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str


class UserResponse(BaseModel):
    """Public customer profile response."""
    id: int
    name: str
    email: str


# ── Route Handlers ────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_sqlite_db)):
    """Register a new customer account, hash their password, and issue a JWT token.

    Args:
        req (RegisterRequest): Registration details (name, email, plaintext password).
        db (Session): SQLAlchemy database session.

    Returns:
        TokenResponse: Access token and customer details.

    Raises:
        HTTPException: 400 Bad Request if the email address is already in use.
    """
    # Verify uniqueness of email address
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash plaintext password securely with bcrypt salt
    user = User(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Issue signed JWT token with user id subject claim
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_sqlite_db)):
    """Authenticate customer credentials and return a signed JWT access token.

    Args:
        req (LoginRequest): Login credentials (email, plaintext password).
        db (Session): SQLAlchemy database session.

    Returns:
        TokenResponse: Signed JWT access token with user identification.

    Raises:
        HTTPException: 401 Unauthorized if email is not found or password does not match.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Issue signed JWT token
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Fetch profile information for the currently authenticated customer.

    Requires:
        Authorization: Bearer <token>

    Args:
        current_user (User): Injected User entity resolved from the JWT token.

    Returns:
        UserResponse: Current user ID, name, and email address.
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
    )

