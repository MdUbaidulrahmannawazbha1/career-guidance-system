"""Prediction schemas for career and placement likelihood models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Career prediction
# ---------------------------------------------------------------------------


class CareerPredictRequest(BaseModel):
    """Input features required to predict suitable careers for a student."""

    cgpa: float
    skills: list[str]
    projects: int
    internship: bool
    backlog: int
    personality_score: Optional[float] = None
    interest_score: Optional[float] = None


class CareerPredictResponse(BaseModel):
    """Predicted careers returned by the career recommendation model."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    predicted_careers: list[dict[str, Any]]
    created_at: datetime


# ---------------------------------------------------------------------------
# Placement prediction
# ---------------------------------------------------------------------------


class PlacementPredictRequest(BaseModel):
    """Input features required to estimate a student's placement probability."""

    cgpa: float
    skills: list[str]
    projects: int
    internship: bool
    backlog: int
    personality_score: Optional[float] = None
    interest_score: Optional[float] = None


class PlacementPredictResponse(BaseModel):
    """Placement likelihood score with actionable weak-area tips."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    probability: float
    weak_areas: list[Any]
    tips: list[Any]
    created_at: datetime


# ---------------------------------------------------------------------------
# What-if simulation
# ---------------------------------------------------------------------------


class SimulateRequest(BaseModel):
    """Input for a what-if simulation showing impact of profile improvements."""

    cgpa: float
    skills: list[str]
    projects: int
    internship: bool
    backlog: int
    personality_score: Optional[float] = None
    interest_score: Optional[float] = None
    skill_increase: float = Field(default=0.0, ge=0)
    cgpa_increase: float = Field(default=0.0, ge=0)


class SimulateResponse(BaseModel):
    """Comparison of original vs. simulated placement/career outcomes."""

    original: dict[str, Any]
    simulated: dict[str, Any]
