import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from app.models.base import Base

# The encryption key is read from the environment at import time.
# Set SECRET_KEY in the environment before starting the application.
import os

_SECRET_KEY = os.getenv("SECRET_KEY")
if not _SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Set a strong random value before starting the application."
    )
"""
User ORM model.

Defines the ``User`` table and the ``UserRole`` enumeration used throughout
the application for authentication and role-based access control.
"""

import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    counsellor = "counsellor"
    mentor = "mentor"
    admin = "admin"


class User(Base):
    """Application user — authentication and role information."""

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    email = Column(
        EncryptedType(String, _SECRET_KEY, AesEngine, "pkcs5"),
        nullable=False,
    )
    hashed_password = Column(String, nullable=False)
    full_name = Column(
        EncryptedType(String, _SECRET_KEY, AesEngine, "pkcs5"),
        nullable=True,
    )
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(
        Enum(UserRole, name="userrole", create_type=True),
        nullable=False,
        default=UserRole.student,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    student_profile = relationship(
        "StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    mentor_profile = relationship(
        "MentorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    career_assessments = relationship(
        "CareerAssessment", back_populates="user", cascade="all, delete-orphan"
    )
    knowledge_assessments = relationship(
        "KnowledgeAssessment", back_populates="user", cascade="all, delete-orphan"
    )
    career_predictions = relationship(
        "CareerPrediction", back_populates="user", cascade="all, delete-orphan"
    )
    placement_predictions = relationship(
        "PlacementPrediction", back_populates="user", cascade="all, delete-orphan"
    )
    resumes = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    skill_gap_analyses = relationship(
        "SkillGapAnalysis", back_populates="user", cascade="all, delete-orphan"
    )
    learning_roadmaps = relationship(
        "LearningRoadmap", back_populates="user", cascade="all, delete-orphan"
    )
    mentorship_sessions_as_student = relationship(
        "MentorshipSession",
        foreign_keys="MentorshipSession.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    mentorship_sessions_as_mentor = relationship(
        "MentorshipSession",
        foreign_keys="MentorshipSession.mentor_id",
        back_populates="mentor",
    )
    sent_messages = relationship(
        "ChatMessage",
        foreign_keys="ChatMessage.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_messages = relationship(
        "ChatMessage",
        foreign_keys="ChatMessage.receiver_id",
        back_populates="receiver",
    )
    audit_logs = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )
    created_questions = relationship(
        "QuestionBank", back_populates="created_by_user"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_created_at", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} role={self.role}>"
