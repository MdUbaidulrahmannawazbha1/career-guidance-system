"""Chat schemas for AI chatbot interactions and peer messaging."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatBotRequest(BaseModel):
    """Request body for sending a message to the AI career chatbot."""

    message: str
    history: list[dict[str, Any]] = Field(default_factory=list)


class ChatBotResponse(BaseModel):
    """AI chatbot reply."""

    reply: str


class ChatSendRequest(BaseModel):
    """Request body for sending a direct message to another user."""

    receiver_id: uuid.UUID
    message: str


class ChatMessageResponse(BaseModel):
    """Persisted direct message between two users."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    message: str
    is_read: bool
    sent_at: datetime
