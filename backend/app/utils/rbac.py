"""
Role-Based Access Control (RBAC) utilities.

Provides the ``require_role`` FastAPI dependency factory.  Use it to restrict
route access to one or more user roles::

    from app.utils.rbac import require_role
    from app.models.user import UserRole

    @router.delete("/admin/users/{user_id}")
    async def delete_user(
        current_user=Depends(require_role(UserRole.admin)),
    ):
        ...
"""

from typing import Any

from fastapi import Depends, HTTPException, status

from app.utils.jwt_handler import get_current_user


def require_role(*roles: str) -> Any:
    """
    Return a FastAPI dependency that enforces role-based access control.

    The dependency calls :func:`~app.utils.jwt_handler.get_current_user` to
    resolve the authenticated user and then checks that their ``role``
    attribute is among the ``roles`` passed to this factory.

    Parameters
    ----------
    *roles:
        One or more role names (strings or ``UserRole`` enum values) that are
        permitted to access the route.

    Returns
    -------
    Callable
        An async FastAPI dependency that either returns the current user or
        raises ``HTTP 403 Forbidden``.

    Raises
    ------
    HTTPException (403)
        If the current user's role is not in the allowed ``roles``.
    """
    allowed = {str(r) for r in roles}

    async def _check_role(current_user: Any = Depends(get_current_user)) -> Any:
        user_role = str(current_user.role)
        # Handle both plain-string values and ``"UserRole.admin"``-style names.
        if user_role not in allowed and user_role.split(".")[-1] not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return _check_role
