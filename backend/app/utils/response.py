"""
Standard API response helpers.

Provides ``success_response`` and ``error_response`` factory functions that
produce consistently structured JSON responses throughout the API.
"""

from typing import Any, Optional

from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> JSONResponse:
    """
    Build a standard success JSON response.

    Parameters
    ----------
    data:
        The payload to include under the ``"data"`` key.
    message:
        A human-readable status message.
    status_code:
        HTTP status code (default: 200).

    Returns
    -------
    JSONResponse
        ``{"success": true, "message": "...", "data": ...}``
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )


def error_response(
    message: str,
    status_code: int = 400,
    detail: Optional[Any] = None,
) -> JSONResponse:
    """
    Build a standard error JSON response.

    Parameters
    ----------
    message:
        A human-readable error description.
    status_code:
        HTTP status code (default: 400).
    detail:
        Optional additional error detail / context.

    Returns
    -------
    JSONResponse
        ``{"success": false, "message": "...", "detail": ...}``
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "detail": detail,
        },
    )
