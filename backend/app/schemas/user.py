"""User and profile schemas for the career guidance system."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """Public representation of a user account."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """Fields that a user may update on their own account."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class StudentProfileResponse(BaseModel):
    """Public representation of a student's academic profile."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    cgpa: Optional[float] = None
    branch: Optional[str] = None
    skills: Optional[list[str]] = None
    projects: Optional[int] = None
    internships: Optional[int] = None
    backlogs: Optional[int] = None
    grad_year: Optional[int] = None
    communication_score: Optional[float] = None


class StudentProfileUpdate(BaseModel):
    """Fields a student may update in their academic profile."""

    cgpa: Optional[float] = None
    branch: Optional[str] = None
    skills: Optional[list[str]] = None
    projects: Optional[int] = None
    internships: Optional[int] = None
    backlogs: Optional[int] = None
    grad_year: Optional[int] = None
    communication_score: Optional[float] = None


class MentorProfileResponse(BaseModel):
    """Public representation of a mentor's professional profile."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    expertise: Optional[list[str]] = None
    company: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    is_approved: bool = False


class UserWithProfileResponse(UserResponse):
    """User account combined with role-specific profile data."""

    student_profile: Optional[StudentProfileResponse] = None
    mentor_profile: Optional[MentorProfileResponse] = None
