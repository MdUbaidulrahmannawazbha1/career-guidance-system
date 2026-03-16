"""
Chat router.

Endpoints
---------
POST /chat/bot                – send a message to the Groq AI career counsellor
POST /chat/send               – send a direct message to another user
GET  /chat/history/{user_id}  – retrieve conversation history with a user
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.chat import ChatBotRequest, ChatSendRequest
from app.utils.jwt_handler import get_current_user
from app.utils.response import success_response

router = APIRouter(prefix="/chat", tags=["chat"])


# ---------------------------------------------------------------------------
# POST /chat/bot
# ---------------------------------------------------------------------------


@router.post("/bot")
async def chat_with_bot(
    body: ChatBotRequest,
    current_user: User = Depends(get_current_user),
):
    """Send a message to the Groq AI career counsellor and receive a reply."""
    from app.ai.chatbot import chat

    try:
        reply = await chat(message=body.message, history=body.history)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return success_response(data={"reply": reply}, message="AI response generated")


# ---------------------------------------------------------------------------
# POST /chat/send
# ---------------------------------------------------------------------------


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_message(
    body: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a direct message to another user (mentor or counsellor)."""
    # Verify receiver exists
    result = await db.execute(select(User).where(User.id == body.receiver_id))
    receiver = result.scalar_one_or_none()
    if receiver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient user not found",
        )

    if receiver.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send a message to yourself",
        )

    msg = ChatMessage(
        sender_id=current_user.id,
        receiver_id=body.receiver_id,
        message=body.message,
        is_read=False,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    return success_response(
        data={
            "id": str(msg.id),
            "sender_id": str(msg.sender_id),
            "receiver_id": str(msg.receiver_id),
            "message": msg.message,
            "is_read": msg.is_read,
            "sent_at": msg.sent_at.isoformat(),
        },
        message="Message sent",
        status_code=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# GET /chat/history/{user_id}
# ---------------------------------------------------------------------------


@router.get("/history/{other_user_id}")
async def get_chat_history(
    other_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the conversation history between the current user and another user."""
    # Verify the other user exists
    result = await db.execute(select(User).where(User.id == other_user_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    stmt = (
        select(ChatMessage)
        .where(
            or_(
                (ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == other_user_id),
                (ChatMessage.sender_id == other_user_id) & (ChatMessage.receiver_id == current_user.id),
            )
        )
        .order_by(ChatMessage.sent_at.asc())
    )
    messages_result = await db.execute(stmt)
    messages = messages_result.scalars().all()

    # Mark unread messages as read
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.is_read = True
    await db.commit()

    data = [
        {
            "id": str(m.id),
            "sender_id": str(m.sender_id),
            "receiver_id": str(m.receiver_id),
            "message": m.message,
            "is_read": m.is_read,
            "sent_at": m.sent_at.isoformat(),
        }
        for m in messages
    ]

    return success_response(data=data, message=f"Found {len(data)} messages")
