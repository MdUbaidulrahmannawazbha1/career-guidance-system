"""
Mentorship router.

Endpoints
---------
GET  /mentor/available   – list approved mentors, optionally filtered by expertise
POST /mentor/request     – student requests a mentor session
PUT  /mentor/respond     – mentor accepts or rejects a session request
GET  /mentor/sessions    – list sessions where the current user is mentor
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.profile import MentorProfile
from app.models.roadmap import MentorshipSession, SessionStatus
from app.models.user import User, UserRole
from app.utils.jwt_handler import get_current_user
from app.utils.rbac import require_role
from app.utils.response import success_response

router = APIRouter(prefix="/mentor", tags=["mentorship"])


# ---------------------------------------------------------------------------
# GET /mentor/available
# ---------------------------------------------------------------------------


@router.get("/available")
async def list_available_mentors(
    expertise: Optional[str] = Query(None, description="Filter by expertise keyword"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all approved mentors, optionally filtered by expertise area."""
    stmt = (
        select(MentorProfile, User)
        .join(User, User.id == MentorProfile.user_id)
        .where(MentorProfile.is_approved == True, User.is_active == True)  # noqa: E712
    )
    result = await db.execute(stmt)
    rows = result.all()

    mentors = []
    for profile, user in rows:
        if expertise and profile.expertise:
            if not any(expertise.lower() in e.lower() for e in profile.expertise):
                continue
        mentors.append(
            {
                "user_id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "expertise": profile.expertise,
                "company": profile.company,
                "experience_years": profile.experience_years,
                "bio": profile.bio,
            }
        )

    return success_response(data=mentors, message=f"Found {len(mentors)} available mentors")


# ---------------------------------------------------------------------------
# POST /mentor/request
# ---------------------------------------------------------------------------


@router.post("/request")
async def request_mentor(
    mentor_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Student creates a pending mentorship session request."""
    import uuid

    # Validate mentor exists and is approved
    mentor_uuid = uuid.UUID(mentor_id)
    result = await db.execute(
        select(MentorProfile).where(
            MentorProfile.user_id == mentor_uuid,
            MentorProfile.is_approved == True,  # noqa: E712
        )
    )
    mentor_profile = result.scalar_one_or_none()
    if mentor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found or not yet approved",
        )

    # Prevent duplicate pending requests
    existing = await db.execute(
        select(MentorshipSession).where(
            MentorshipSession.student_id == current_user.id,
            MentorshipSession.mentor_id == mentor_uuid,
            MentorshipSession.status == SessionStatus.pending,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending request to this mentor already exists",
        )

    session = MentorshipSession(
        student_id=current_user.id,
        mentor_id=mentor_uuid,
        status=SessionStatus.pending,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return success_response(
        data={
            "id": str(session.id),
            "mentor_id": str(session.mentor_id),
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
        },
        message="Mentorship request sent",
        status_code=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# PUT /mentor/respond
# ---------------------------------------------------------------------------


@router.put("/respond")
async def respond_to_request(
    session_id: str,
    accept: bool,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mentor accepts or rejects a pending session request."""
    import uuid

    session_uuid = uuid.UUID(session_id)
    result = await db.execute(
        select(MentorshipSession).where(
            MentorshipSession.id == session_uuid,
            MentorshipSession.mentor_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or you are not the assigned mentor",
        )

    if session.status != SessionStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending sessions can be accepted or rejected",
        )

    session.status = SessionStatus.active if accept else SessionStatus.rejected
    await db.commit()
    await db.refresh(session)

    return success_response(
        data={
            "id": str(session.id),
            "status": session.status.value,
        },
        message="Session " + ("accepted" if accept else "rejected"),
    )


# ---------------------------------------------------------------------------
# GET /mentor/sessions
# ---------------------------------------------------------------------------


@router.get("/sessions")
async def list_mentor_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all active mentorship sessions for the current user (as mentor)."""
    result = await db.execute(
        select(MentorshipSession).where(
            MentorshipSession.mentor_id == current_user.id,
            MentorshipSession.status == SessionStatus.active,
        )
    )
    sessions = result.scalars().all()

    data = [
        {
            "id": str(s.id),
            "student_id": str(s.student_id),
            "status": s.status.value,
            "notes": s.notes,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]

    return success_response(data=data, message=f"Found {len(data)} active sessions")
