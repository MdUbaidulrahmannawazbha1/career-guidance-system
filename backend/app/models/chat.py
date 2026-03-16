import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ChatMessage(Base):
    """Direct message sent between two users."""

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    receiver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    sent_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------ #
    # Relationships                                                         #
    # ------------------------------------------------------------------ #
    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages",
    )
    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages",
    )

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_chat_messages_sender_id", "sender_id"),
        Index("ix_chat_messages_receiver_id", "receiver_id"),
        Index("ix_chat_messages_sent_at", "sent_at"),
        Index("ix_chat_messages_is_read", "is_read"),
        # Composite index for conversation queries
        Index("ix_chat_messages_conversation", "sender_id", "receiver_id", "sent_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ChatMessage sender_id={self.sender_id} "
            f"receiver_id={self.receiver_id} is_read={self.is_read}>"
        )
