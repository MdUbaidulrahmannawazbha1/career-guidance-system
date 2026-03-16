"""
JWT token utilities.

Provides helpers for creating and verifying access / refresh tokens and a
FastAPI dependency that resolves the current authenticated user from the
Authorization header.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Token type constants used in the ``type`` claim.
_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"


def _build_token(
    data: Dict[str, Any],
    token_type: str,
    expires_delta: timedelta,
) -> str:
    """Encode a JWT with an expiry and a ``type`` claim."""
    payload = data.copy()
    payload["type"] = token_type
    payload["exp"] = datetime.now(tz=timezone.utc) + expires_delta
    payload["iat"] = datetime.now(tz=timezone.utc)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Parameters
    ----------
    data:
        Payload dict (must include a ``sub`` claim identifying the user).
    expires_delta:
        Optional custom lifetime; defaults to ``ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns
    -------
    str
        Encoded JWT string.
    """
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _build_token(data, _ACCESS_TYPE, delta)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a signed JWT refresh token with a 7-day lifetime.

    Parameters
    ----------
    data:
        Payload dict (must include a ``sub`` claim identifying the user).

    Returns
    -------
    str
        Encoded JWT string.
    """
    delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _build_token(data, _REFRESH_TYPE, delta)


def verify_token(token: str, expected_type: str = _ACCESS_TYPE) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Parameters
    ----------
    token:
        Raw JWT string.
    expected_type:
        Token type to enforce (``"access"`` or ``"refresh"``).

    Returns
    -------
    dict
        Decoded payload.

    Raises
    ------
    HTTPException (401)
        If the token is invalid, expired, or the wrong type.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: Dict[str, Any] = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        raise credentials_exception

    if payload.get("type") != expected_type:
        raise credentials_exception

    if payload.get("sub") is None:
        raise credentials_exception

    return payload


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    FastAPI dependency that resolves the authenticated user from a Bearer token.

    Parameters
    ----------
    token:
        JWT Bearer token extracted from the ``Authorization`` header.
    db:
        Async database session (injected by FastAPI).

    Returns
    -------
    User
        The ORM ``User`` instance corresponding to the token subject.

    Raises
    ------
    HTTPException (401)
        If the token is invalid or the user does not exist / is inactive.
    """
    # Import here to avoid circular imports at module level.
    from app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token, expected_type=_ACCESS_TYPE)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user
