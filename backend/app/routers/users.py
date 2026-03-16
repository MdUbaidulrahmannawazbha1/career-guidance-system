"""
Users router.

Endpoints
---------
GET  /users/me                    – return current user profile (decrypted)
PUT  /users/me                    – update profile fields
PUT  /users/me/student-profile    – update student academic data
GET  /users/students              – counsellor / admin: list assigned students
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.profile import StudentProfile
from app.models.user import User, UserRole
from app.schemas.user import (
    StudentProfileResponse,
    StudentProfileUpdate,
    UserResponse,
    UserUpdate,
    UserWithProfileResponse,
)
from app.utils.jwt_handler import get_current_user
from app.utils.rbac import require_role
from app.utils.response import success_response

router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------


@router.get("/me", response_model=UserWithProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return current_user


# ---------------------------------------------------------------------------
# PUT /users/me
# ---------------------------------------------------------------------------


@router.put("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile (full_name and/or email)."""
    if body.email is not None:
        # Ensure email is not already taken by another user
        result = await db.execute(
            select(User).where(User.email == body.email.lower(), User.id != current_user.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already in use",
            )
        current_user.email = body.email.lower()

    if body.full_name is not None:
        current_user.full_name = body.full_name

    await db.commit()
    await db.refresh(current_user)
    return current_user


# ---------------------------------------------------------------------------
# PUT /users/me/student-profile
# ---------------------------------------------------------------------------


@router.put("/me/student-profile", response_model=StudentProfileResponse)
async def update_student_profile(
    body: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update the current student's academic profile."""
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# GET /users/students  (counsellor / admin only)
# ---------------------------------------------------------------------------


@router.get("/students")
async def list_students(
    current_user: User = Depends(require_role(UserRole.counsellor, UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Return a list of all student users with their profiles."""
    result = await db.execute(select(User).where(User.role == UserRole.student))
    students = result.scalars().all()

    data = []
    for student in students:
        student_dict = {
            "id": str(student.id),
            "email": student.email,
            "full_name": student.full_name,
            "role": student.role.value,
            "is_active": student.is_active,
            "created_at": student.created_at.isoformat() if student.created_at else None,
        }
        # Load student profile if available
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == student.id)
        )
        profile = profile_result.scalar_one_or_none()
        if profile:
            student_dict["student_profile"] = {
                "cgpa": profile.cgpa,
                "branch": profile.branch,
                "skills": profile.skills,
                "grad_year": profile.grad_year,
            }
        data.append(student_dict)

    return success_response(data=data, message=f"Found {len(data)} students")
