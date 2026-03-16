"""Authentication schemas for registration, login, and token management."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """Request body for new user registration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class LoginRequest(BaseModel):
    """Request body for user login."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """Response body containing JWT access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Request body for refreshing an access token."""

    refresh_token: str


class GoogleCallbackRequest(BaseModel):
    """Request body for Google OAuth callback."""

    code: str
    state: Optional[str] = None
