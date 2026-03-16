"""
SQLAlchemy ORM models for the Career Guidance System.

Import order matters: Base must be imported before any model so that
all mapper configurations are registered on the same metadata object.
"""

from app.models.base import Base  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401
from app.models.profile import StudentProfile, MentorProfile  # noqa: F401
from app.models.assessment import CareerAssessment, KnowledgeAssessment  # noqa: F401
from app.models.prediction import CareerPrediction, PlacementPrediction  # noqa: F401
from app.models.analysis import Resume, SkillGapAnalysis  # noqa: F401
from app.models.roadmap import LearningRoadmap, MentorshipSession, SessionStatus  # noqa: F401
from app.models.chat import ChatMessage  # noqa: F401
from app.models.admin import QuestionBank, CareerSkillsMap, AuditLog, Difficulty  # noqa: F401

__all__ = [
    "Base",
    # User
    "User",
    "UserRole",
    # Profiles
    "StudentProfile",
    "MentorProfile",
    # Assessments
    "CareerAssessment",
    "KnowledgeAssessment",
    # Predictions
    "CareerPrediction",
    "PlacementPrediction",
    # Analysis
    "Resume",
    "SkillGapAnalysis",
    # Roadmaps & Mentorship
    "LearningRoadmap",
    "MentorshipSession",
    "SessionStatus",
    # Chat
    "ChatMessage",
    # Admin
    "QuestionBank",
    "CareerSkillsMap",
    "AuditLog",
    "Difficulty",
]
