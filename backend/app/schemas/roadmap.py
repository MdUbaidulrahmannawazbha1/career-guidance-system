"""Roadmap and mentorship session schemas for the career guidance system."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class RoadmapGenerateRequest(BaseModel):
    """Request body for generating a personalised learning roadmap."""

    target_career: str
    hours_per_week: int = Field(default=10, gt=0)
    target_date: Optional[date] = None


class WeekPlan(BaseModel):
    """Plan for a single week within a learning roadmap."""

    week: int
    topic: str
    skills_covered: list[str]
    resources: list[str]
    mini_project: str
    estimated_hours: int


class RoadmapResponse(BaseModel):
    """A generated learning roadmap with week-by-week plan and progress."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    target_career: str
    weeks_plan: list[WeekPlan]
    progress: dict[str, Any]
    created_at: datetime


class RoadmapProgressUpdate(BaseModel):
    """Request body to mark a roadmap week as complete (or incomplete)."""

    week_number: int
    completed: bool = True


class MentorshipSessionResponse(BaseModel):
    """Details of a mentorship session between a student and a mentor."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    student_id: uuid.UUID
    mentor_id: uuid.UUID
    status: str
    notes: Optional[str] = None
    created_at: datetime
