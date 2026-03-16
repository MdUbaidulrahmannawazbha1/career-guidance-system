import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class CareerAssessment(Base):
    """Results of a personality / interest career assessment."""

    __tablename__ = "career_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    answers = Column(JSONB, nullable=True)
    personality_type = Column(String(50), nullable=True)
    interest_scores = Column(JSONB, nullable=True)
    taken_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="career_assessments")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_career_assessments_user_id", "user_id"),
        Index("ix_career_assessments_taken_at", "taken_at"),
        Index("ix_career_assessments_personality_type", "personality_type"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CareerAssessment user_id={self.user_id} personality_type={self.personality_type}>"


class KnowledgeAssessment(Base):
    """Results of a topic-based knowledge quiz."""

    __tablename__ = "knowledge_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic = Column(String(255), nullable=False)
    difficulty = Column(String(50), nullable=True)
    score = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=True)
    answers = Column(JSONB, nullable=True)
    taken_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="knowledge_assessments")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_knowledge_assessments_user_id", "user_id"),
        Index("ix_knowledge_assessments_topic", "topic"),
        Index("ix_knowledge_assessments_taken_at", "taken_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<KnowledgeAssessment user_id={self.user_id} topic={self.topic} score={self.score}>"
        )
