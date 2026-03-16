"""
AuditLog ORM model.

Records every mutating request (POST / PUT / DELETE) for compliance and
debugging.  Written automatically by ``AuditMiddleware``.

The canonical definition lives in :pymod:`app.models.admin`.  This module
re-exports the class so that existing ``from app.models.audit_log import
AuditLog`` imports continue to work.
"""

from app.models.admin import AuditLog  # noqa: F401

__all__ = ["AuditLog"]
