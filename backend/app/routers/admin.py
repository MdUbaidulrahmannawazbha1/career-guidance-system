"""
Admin router.

Endpoints
---------
GET    /admin/users                  – paginated user list
PUT    /admin/users/{id}/role        – change a user's role
PUT    /admin/users/{id}/status      – activate / deactivate a user
GET    /admin/analytics              – full analytics data
GET    /admin/mentors/pending        – list unapproved mentor applications
PUT    /admin/mentors/{id}/approve   – approve a mentor
POST   /admin/questions              – create a question bank entry
PUT    /admin/questions/{id}         – update a question bank entry
DELETE /admin/questions/{id}         – delete a question bank entry
POST   /admin/careers                – add a career → skills mapping
GET    /admin/audit-logs             – paginated audit log
GET    /admin/export/users           – CSV download of all users
GET    /admin/export/analytics       – CSV download of analytics
"""

import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.admin import AuditLog, CareerSkillsMap, QuestionBank
from app.models.assessment import CareerAssessment
from app.models.prediction import CareerPrediction, PlacementPrediction
from app.models.profile import MentorProfile
from app.models.user import User, UserRole
from app.schemas.admin import (
    CareerSkillCreate,
    QuestionCreate,
    QuestionUpdate,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.utils.rbac import require_role
from app.utils.response import success_response

router = APIRouter(prefix="/admin", tags=["admin"])

_admin_dep = Depends(require_role(UserRole.admin))


# ---------------------------------------------------------------------------
# GET /admin/users
# ---------------------------------------------------------------------------


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str | None = None,
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Return a paginated list of all users."""
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()

    data = [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]

    return success_response(
        data={"items": data, "total": total, "page": page, "page_size": page_size},
        message="Users retrieved",
    )


# ---------------------------------------------------------------------------
# PUT /admin/users/{id}/role
# ---------------------------------------------------------------------------


@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: uuid.UUID,
    body: UserRoleUpdate,
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Change a user's role."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        target.role = UserRole(body.role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role: {body.role}")

    await db.commit()
    return success_response(
        data={"id": str(target.id), "role": target.role.value},
        message="Role updated",
    )


# ---------------------------------------------------------------------------
# PUT /admin/users/{id}/status
# ---------------------------------------------------------------------------


@router.put("/users/{user_id}/status")
async def change_user_status(
    user_id: uuid.UUID,
    body: UserStatusUpdate,
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Activate or deactivate a user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    target.is_active = body.is_active
    await db.commit()
    return success_response(
        data={"id": str(target.id), "is_active": target.is_active},
        message="Status updated",
    )


# ---------------------------------------------------------------------------
# GET /admin/analytics
# ---------------------------------------------------------------------------


@router.get("/analytics")
async def get_analytics(
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Return aggregate analytics across the platform."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_students = (
        await db.execute(select(func.count(User.id)).where(User.role == UserRole.student))
    ).scalar_one()
    total_mentors = (
        await db.execute(select(func.count(User.id)).where(User.role == UserRole.mentor))
    ).scalar_one()
    total_assessments = (await db.execute(select(func.count(CareerAssessment.id)))).scalar_one()
    total_predictions = (await db.execute(select(func.count(CareerPrediction.id)))).scalar_one()
    total_placement = (await db.execute(select(func.count(PlacementPrediction.id)))).scalar_one()

    return success_response(
        data={
            "total_users": total_users,
            "total_students": total_students,
            "total_mentors": total_mentors,
            "total_career_assessments": total_assessments,
            "total_career_predictions": total_predictions,
            "total_placement_predictions": total_placement,
        },
        message="Analytics retrieved",
    )


# ---------------------------------------------------------------------------
# GET /admin/mentors/pending
# ---------------------------------------------------------------------------


@router.get("/mentors/pending")
async def list_pending_mentors(
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Return all mentor applications pending admin approval."""
    stmt = (
        select(MentorProfile, User)
        .join(User, User.id == MentorProfile.user_id)
        .where(MentorProfile.is_approved == False)  # noqa: E712
    )
    result = await db.execute(stmt)
    rows = result.all()

    data = [
        {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "expertise": profile.expertise,
            "company": profile.company,
            "experience_years": profile.experience_years,
            "bio": profile.bio,
        }
        for profile, user in rows
    ]

    return success_response(data=data, message=f"Found {len(data)} pending mentors")


# ---------------------------------------------------------------------------
# PUT /admin/mentors/{id}/approve
# ---------------------------------------------------------------------------


@router.put("/mentors/{mentor_user_id}/approve")
async def approve_mentor(
    mentor_user_id: uuid.UUID,
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Approve a mentor's profile so they appear in the available mentor list."""
    result = await db.execute(
        select(MentorProfile).where(MentorProfile.user_id == mentor_user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor profile not found")

    profile.is_approved = True
    await db.commit()
    return success_response(
        data={"user_id": str(mentor_user_id), "is_approved": True},
        message="Mentor approved",
    )


# ---------------------------------------------------------------------------
# POST /admin/questions
# ---------------------------------------------------------------------------


@router.post("/questions", status_code=status.HTTP_201_CREATED)
async def create_question(
    body: QuestionCreate,
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Add a new question to the question bank."""
    from app.models.admin import Difficulty

    try:
        diff = Difficulty(body.difficulty.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid difficulty '{body.difficulty}'. Must be easy, medium or hard.",
        )

    question = QuestionBank(
        topic=body.topic,
        difficulty=diff,
        question=body.question,
        options=body.options,
        correct_answer=body.correct_answer,
        created_by=current_user.id,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)

    return success_response(
        data={
            "id": str(question.id),
            "topic": question.topic,
            "difficulty": question.difficulty.value,
            "question": question.question,
        },
        message="Question created",
        status_code=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# PUT /admin/questions/{id}
# ---------------------------------------------------------------------------


@router.put("/questions/{question_id}")
async def update_question(
    question_id: uuid.UUID,
    body: QuestionUpdate,
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing question bank entry."""
    result = await db.execute(select(QuestionBank).where(QuestionBank.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    update_data = body.model_dump(exclude_none=True)
    if "difficulty" in update_data:
        from app.models.admin import Difficulty

        try:
            update_data["difficulty"] = Difficulty(update_data["difficulty"].lower())
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid difficulty")

    for field, value in update_data.items():
        setattr(question, field, value)

    await db.commit()
    await db.refresh(question)
    return success_response(
        data={"id": str(question.id), "topic": question.topic},
        message="Question updated",
    )


# ---------------------------------------------------------------------------
# DELETE /admin/questions/{id}
# ---------------------------------------------------------------------------


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: uuid.UUID,
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Delete a question from the question bank."""
    result = await db.execute(select(QuestionBank).where(QuestionBank.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    await db.delete(question)
    await db.commit()


# ---------------------------------------------------------------------------
# POST /admin/careers
# ---------------------------------------------------------------------------


@router.post("/careers", status_code=status.HTTP_201_CREATED)
async def create_career_skills(
    body: CareerSkillCreate,
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Add a career → required skills mapping to the database."""
    # Check for duplicate career name
    existing = await db.execute(
        select(CareerSkillsMap).where(CareerSkillsMap.career_name == body.career_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Career '{body.career_name}' already exists",
        )

    career_map = CareerSkillsMap(
        career_name=body.career_name,
        required_skills=body.required_skills,
        resources=body.resources,
        avg_salary=body.avg_salary,
    )
    db.add(career_map)
    await db.commit()
    await db.refresh(career_map)

    return success_response(
        data={
            "id": str(career_map.id),
            "career_name": career_map.career_name,
            "required_skills": career_map.required_skills,
        },
        message="Career skills mapping created",
        status_code=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# GET /admin/audit-logs
# ---------------------------------------------------------------------------


@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Return paginated audit log entries."""
    count_result = await db.execute(select(func.count(AuditLog.id)))
    total = count_result.scalar_one()

    stmt = (
        select(AuditLog)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(AuditLog.timestamp.desc())
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    data = [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "endpoint": log.endpoint,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        for log in logs
    ]

    return success_response(
        data={"items": data, "total": total, "page": page, "page_size": page_size},
        message="Audit logs retrieved",
    )


# ---------------------------------------------------------------------------
# GET /admin/export/users  – CSV download
# ---------------------------------------------------------------------------


@router.get("/export/users")
async def export_users_csv(
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Download all users as a CSV file."""
    result = await db.execute(select(User).order_by(User.created_at))
    users = result.scalars().all()

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "email", "full_name", "role", "is_active", "created_at"],
    )
    writer.writeheader()
    for u in users:
        writer.writerow(
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name or "",
                "role": u.role.value,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else "",
            }
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"},
    )


# ---------------------------------------------------------------------------
# GET /admin/export/analytics  – CSV download
# ---------------------------------------------------------------------------


@router.get("/export/analytics")
async def export_analytics_csv(
    current_user: User = _admin_dep,
    db: AsyncSession = Depends(get_db),
):
    """Download platform analytics as a CSV file."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_students = (
        await db.execute(select(func.count(User.id)).where(User.role == UserRole.student))
    ).scalar_one()
    total_mentors = (
        await db.execute(select(func.count(User.id)).where(User.role == UserRole.mentor))
    ).scalar_one()
    total_assessments = (await db.execute(select(func.count(CareerAssessment.id)))).scalar_one()
    total_predictions = (await db.execute(select(func.count(CareerPrediction.id)))).scalar_one()
    total_placement = (await db.execute(select(func.count(PlacementPrediction.id)))).scalar_one()

    rows = [
        {"metric": "total_users", "value": total_users},
        {"metric": "total_students", "value": total_students},
        {"metric": "total_mentors", "value": total_mentors},
        {"metric": "total_career_assessments", "value": total_assessments},
        {"metric": "total_career_predictions", "value": total_predictions},
        {"metric": "total_placement_predictions", "value": total_placement},
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["metric", "value"])
    writer.writeheader()
    writer.writerows(rows)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics.csv"},
    )
