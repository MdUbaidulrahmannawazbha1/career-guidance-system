import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class StudentProfile(Base):
    """Academic and co-curricular details for student users."""

    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    cgpa = Column(Float, nullable=True)
    branch = Column(String(255), nullable=True)
    skills = Column(ARRAY(String), nullable=True)
    projects = Column(Integer, nullable=True)
    internships = Column(Integer, nullable=True)
    backlogs = Column(Integer, nullable=True)
    grad_year = Column(Integer, nullable=True)
    communication_score = Column(Float, nullable=True)

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="student_profile")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_student_profiles_user_id", "user_id"),
        Index("ix_student_profiles_branch", "branch"),
        Index("ix_student_profiles_grad_year", "grad_year"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<StudentProfile user_id={self.user_id} branch={self.branch}>"


class MentorProfile(Base):
    """Professional details for mentor users."""

    __tablename__ = "mentor_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    expertise = Column(ARRAY(String), nullable=True)
    company = Column(String(255), nullable=True)
    experience_years = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    is_approved = Column(Boolean, nullable=False, default=False)

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="mentor_profile")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_mentor_profiles_user_id", "user_id"),
        Index("ix_mentor_profiles_is_approved", "is_approved"),
        Index("ix_mentor_profiles_company", "company"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MentorProfile user_id={self.user_id} company={self.company}>"
