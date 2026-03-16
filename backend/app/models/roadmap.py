import enum
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class LearningRoadmap(Base):
    """Week-by-week learning plan towards a target career."""

    __tablename__ = "learning_roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_career = Column(String(255), nullable=False)
    weeks_plan = Column(JSONB, nullable=True)
    progress = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="learning_roadmaps")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_learning_roadmaps_user_id", "user_id"),
        Index("ix_learning_roadmaps_target_career", "target_career"),
        Index("ix_learning_roadmaps_created_at", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LearningRoadmap user_id={self.user_id} target_career={self.target_career}>"


class SessionStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    rejected = "rejected"


class MentorshipSession(Base):
    """One-on-one session between a student and a mentor."""

    __tablename__ = "mentorship_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mentor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status = Column(
        Enum(SessionStatus, name="sessionstatus", create_type=True),
        nullable=False,
        default=SessionStatus.pending,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    student = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="mentorship_sessions_as_student",
    )
    mentor = relationship(
        "User",
        foreign_keys=[mentor_id],
        back_populates="mentorship_sessions_as_mentor",
    )

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_mentorship_sessions_student_id", "student_id"),
        Index("ix_mentorship_sessions_mentor_id", "mentor_id"),
        Index("ix_mentorship_sessions_status", "status"),
        Index("ix_mentorship_sessions_created_at", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<MentorshipSession student_id={self.student_id} "
            f"mentor_id={self.mentor_id} status={self.status}>"
        )
