import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class CareerPrediction(Base):
    """ML-generated career path predictions for a student."""

    __tablename__ = "career_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    predicted_careers = Column(JSONB, nullable=True)
    confidence_scores = Column(JSONB, nullable=True)
    input_features = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="career_predictions")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_career_predictions_user_id", "user_id"),
        Index("ix_career_predictions_created_at", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CareerPrediction user_id={self.user_id}>"


class PlacementPrediction(Base):
    """ML-generated campus placement probability for a student."""

    __tablename__ = "placement_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    probability = Column(Float, nullable=True)
    weak_areas = Column(JSONB, nullable=True)
    input_features = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    user = relationship("User", back_populates="placement_predictions")

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_placement_predictions_user_id", "user_id"),
        Index("ix_placement_predictions_created_at", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PlacementPrediction user_id={self.user_id} probability={self.probability}>"
