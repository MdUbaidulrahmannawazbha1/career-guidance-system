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
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Resume(Base):
    """Uploaded resume with parsed content and quality score."""

    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path = Column(String(512), nullable=False)
    extracted_skills = Column(JSONB, nullable=True)
    extracted_education = Column(JSONB, nullable=True)
    extracted_experience = Column(JSONB, nullable=True)
    score = Column(Integer, nullable=True)
    suggestions = Column(JSONB, nullable=True)
    uploaded_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="resumes")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_resumes_user_id", "user_id"),
        Index("ix_resumes_uploaded_at", "uploaded_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Resume user_id={self.user_id} score={self.score}>"


class SkillGapAnalysis(Base):
    """Gap between a student's current skills and a target career."""

    __tablename__ = "skill_gap_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_career = Column(String(255), nullable=False)
    current_skills = Column(ARRAY(String), nullable=True)
    missing_skills = Column(JSONB, nullable=True)
    resources = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="skill_gap_analyses")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_skill_gap_analysis_user_id", "user_id"),
        Index("ix_skill_gap_analysis_target_career", "target_career"),
        Index("ix_skill_gap_analysis_created_at", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SkillGapAnalysis user_id={self.user_id} target_career={self.target_career}>"
