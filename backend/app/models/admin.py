import enum
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionBank(Base):
    """Assessment questions stored centrally by admins / counsellors."""

    __tablename__ = "question_bank"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    topic = Column(String(255), nullable=False)
    difficulty = Column(
        Enum(Difficulty, name="difficulty", create_type=True),
        nullable=False,
    )
    question = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)
    correct_answer = Column(String(512), nullable=False)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    created_by_user = relationship("User", back_populates="created_questions")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_question_bank_topic", "topic"),
        Index("ix_question_bank_difficulty", "difficulty"),
        Index("ix_question_bank_created_by", "created_by"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<QuestionBank topic={self.topic} difficulty={self.difficulty}>"


class CareerSkillsMap(Base):
    """Canonical mapping of careers to required skills and resources."""

    __tablename__ = "career_skills_map"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    career_name = Column(String(255), nullable=False)
    required_skills = Column(ARRAY(String), nullable=True)
    resources = Column(JSONB, nullable=True)
    avg_salary = Column(String(100), nullable=True)

    # ------------------------------------------------------------------ #
    # Indexes / Constraints                                                #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        UniqueConstraint("career_name", name="uq_career_skills_map_career_name"),
        Index("ix_career_skills_map_career_name", "career_name"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CareerSkillsMap career_name={self.career_name}>"


class AuditLog(Base):
    """Immutable record of user actions for compliance and debugging."""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action = Column(String(255), nullable=False)
    endpoint = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="audit_logs")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_timestamp", "timestamp"),
        Index("ix_audit_logs_ip_address", "ip_address"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AuditLog user_id={self.user_id} action={self.action}>"
