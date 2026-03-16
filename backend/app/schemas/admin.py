"""Admin schemas for user management, question bank, and audit logs."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------


class UserRoleUpdate(BaseModel):
    """Update the role of a user account."""

    role: Literal["student", "counsellor", "mentor", "admin"]


class UserStatusUpdate(BaseModel):
    """Activate or deactivate a user account."""

    is_active: bool


# ---------------------------------------------------------------------------
# Question bank
# ---------------------------------------------------------------------------


class QuestionCreate(BaseModel):
    """Payload for adding a new question to the knowledge question bank."""

    topic: str
    difficulty: Literal["easy", "medium", "hard"]
    question: str
    options: list[Any]
    correct_answer: str


class QuestionUpdate(BaseModel):
    """Partial update for an existing question bank entry."""

    topic: Optional[str] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    question: Optional[str] = None
    options: Optional[list[Any]] = None
    correct_answer: Optional[str] = None


class QuestionResponse(BaseModel):
    """A question bank entry as returned by the API."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    topic: str
    difficulty: str
    question: str
    options: list[Any]
    created_by: Optional[uuid.UUID] = None


# ---------------------------------------------------------------------------
# Career skills map
# ---------------------------------------------------------------------------


class CareerSkillCreate(BaseModel):
    """Payload for creating a career-to-skills mapping entry."""

    career_name: str
    required_skills: list[str]
    resources: Optional[dict[str, Any]] = None
    avg_salary: Optional[str] = None


class CareerSkillResponse(BaseModel):
    """A career-to-skills mapping as returned by the API."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    career_name: str
    required_skills: list[str]
    resources: Optional[dict[str, Any]] = None
    avg_salary: Optional[str] = None


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


class AuditLogResponse(BaseModel):
    """A single audit log entry recording user activity."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime


# ---------------------------------------------------------------------------
# Generic pagination wrapper
# ---------------------------------------------------------------------------


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response."""

    items: list[T]
    total: int
    page: int
    page_size: int
