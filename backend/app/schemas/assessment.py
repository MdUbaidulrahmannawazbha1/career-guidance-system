"""Assessment schemas for career interest and knowledge evaluations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Career assessment
# ---------------------------------------------------------------------------


class CareerQuestion(BaseModel):
    """A single question in the career interest assessment."""

    id: str
    question: str
    options: list[str]
    category: str


class CareerAssessmentStartResponse(BaseModel):
    """Payload returned when a career assessment session is started."""

    questions: list[CareerQuestion]


class CareerAnswerItem(BaseModel):
    """A student's answer to one career assessment question."""

    question_id: str
    answer: str


class CareerAssessmentSubmit(BaseModel):
    """Request body for submitting a completed career assessment."""

    answers: list[CareerAnswerItem]


class CareerAssessmentResponse(BaseModel):
    """Result returned after a career assessment is scored."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    personality_type: str
    interest_scores: dict[str, Any]
    taken_at: datetime


# ---------------------------------------------------------------------------
# Knowledge assessment
# ---------------------------------------------------------------------------


class KnowledgeQuestion(BaseModel):
    """A single multiple-choice question in a knowledge assessment."""

    id: str
    topic: str
    difficulty: str
    question: str
    options: list[Any]


class KnowledgeAssessmentStartResponse(BaseModel):
    """Payload returned when a knowledge assessment session is started."""

    questions: list[KnowledgeQuestion]
    topic: str
    difficulty: str


class KnowledgeAnswerItem(BaseModel):
    """A student's answer to one knowledge assessment question."""

    question_id: str
    answer: str


class KnowledgeAssessmentSubmit(BaseModel):
    """Request body for submitting a completed knowledge assessment."""

    topic: str
    difficulty: str
    answers: list[KnowledgeAnswerItem]


class KnowledgeAssessmentResponse(BaseModel):
    """Result returned after a knowledge assessment is scored."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    topic: str
    difficulty: str
    score: int
    total_questions: int
    level: str
    taken_at: datetime
