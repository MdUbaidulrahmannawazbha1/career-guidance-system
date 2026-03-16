"""
Authentication middleware.

Verifies the JWT Bearer token on every incoming request that carries an
``Authorization`` header and attaches the resolved ``User`` instance to
``request.state.current_user``.

Routes that do NOT require authentication (e.g. ``/auth/login``,
``/health``, OpenAPI docs) are enumerated in ``_PUBLIC_PATHS``.
"""

from typing import Set

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import AsyncSessionLocal
from app.utils.jwt_handler import verify_token

# Paths that do not require a valid JWT.
_PUBLIC_PATHS: Set[str] = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    f"{settings.api_v1_prefix}/auth/login",
    f"{settings.api_v1_prefix}/auth/register",
    f"{settings.api_v1_prefix}/auth/refresh",
    f"{settings.api_v1_prefix}/auth/google",
    f"{settings.api_v1_prefix}/auth/google/callback",
}


def _is_public(path: str) -> bool:
    """Return *True* when *path* does not require authentication."""
    if path in _PUBLIC_PATHS:
        return True
    # Allow any sub-path under the OAuth callback prefix.
    return path.startswith(f"{settings.api_v1_prefix}/auth/google")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that validates JWT tokens and populates request state.

    For protected routes the middleware:

    1. Extracts the Bearer token from the ``Authorization`` header.
    2. Calls :func:`~app.utils.jwt_handler.verify_token` to decode it.
    3. Queries the database for the matching ``User`` record.
    4. Attaches the user to ``request.state.current_user``.

    Public routes pass through without any token check.
    """

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request.state.current_user = None

        if _is_public(request.url.path):
            return await call_next(request)

        auth_header: str = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Missing or invalid Authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            payload = verify_token(token)
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Token subject missing"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Lazy import avoids circular dependencies at module level.
        from app.models.user import User

        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"success": False, "message": "Database unavailable"},
            )

        if user is None or not user.is_active:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "User not found or inactive"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.current_user = user
        return await call_next(request)
