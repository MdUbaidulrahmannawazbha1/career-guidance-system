"""
Audit logging middleware.

Automatically records every POST, PUT, PATCH, and DELETE request to the
``audit_logs`` table.  The log entry captures:

* ``user_id``   – resolved from ``request.state.current_user`` (set by
  :class:`~app.middleware.auth_middleware.AuthMiddleware`); ``None`` for
  unauthenticated requests.
* ``action``    – HTTP method + path (e.g. ``"POST /api/v1/auth/login"``).
* ``endpoint``  – the full request path.
* ``ip_address``– the client IP (respects ``X-Forwarded-For`` if present).
* ``timestamp`` – recorded by the database server via ``server_default``.

The write is performed in a fire-and-forget background task so that
audit-log failures never affect the response returned to the client.
"""

import asyncio
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

_AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP, honouring ``X-Forwarded-For``."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


async def _write_audit_log(
    user_id,
    action: str,
    endpoint: str,
    ip_address: str,
) -> None:
    """Persist a single audit log row, ignoring any database errors."""
    from app.models.audit_log import AuditLog

    try:
        async with AsyncSessionLocal() as db:
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                endpoint=endpoint,
                ip_address=ip_address,
            )
            db.add(log_entry)
            await db.commit()
    except Exception:
        logger.exception("Failed to write audit log for action=%s endpoint=%s", action, endpoint)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that logs every mutating HTTP request to the database.

    Only ``POST``, ``PUT``, ``PATCH``, and ``DELETE`` requests are recorded.
    The audit write is submitted as a background task after the response is
    sent so it never blocks the request/response cycle.
    """

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        response = await call_next(request)

        if request.method not in _AUDITED_METHODS:
            return response

        user = getattr(request.state, "current_user", None)
        user_id = getattr(user, "id", None)
        action = f"{request.method} {request.url.path}"
        endpoint = request.url.path
        ip_address = _get_client_ip(request)

        # Fire-and-forget: schedule the coroutine as a task so the response
        # is not delayed.  create_task is preferred over ensure_future for
        # better task management and exception visibility.
        asyncio.create_task(
            _write_audit_log(user_id, action, endpoint, ip_address)
        )

        return response
