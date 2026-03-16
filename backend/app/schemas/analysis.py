"""Analysis schemas for resume parsing and skill-gap identification."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ResumeAnalysisResponse(BaseModel):
    """Result of parsing and scoring an uploaded resume."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    file_path: str
    extracted_skills: list[Any]
    extracted_education: list[Any]
    extracted_experience: list[Any]
    score: int
    suggestions: list[Any]
    uploaded_at: datetime


class SkillGapRequest(BaseModel):
    """Request body for a skill-gap analysis against a target career."""

    target_career: str
    current_skills: list[str]


class SkillGapResponse(BaseModel):
    """Skill-gap analysis result with missing skills and learning resources."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    target_career: str
    have_skills: list[str]
    missing_skills: list[str]
    resources: Optional[dict[str, Any]] = None
    created_at: datetime
