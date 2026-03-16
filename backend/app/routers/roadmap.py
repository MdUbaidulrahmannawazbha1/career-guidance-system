"""
Roadmap router.

Endpoints
---------
POST /roadmap/generate    – generate week-by-week plan, save
GET  /roadmap/me          – get the current user's latest roadmap
PUT  /roadmap/progress    – mark a week as complete
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.roadmap import LearningRoadmap
from app.models.user import User
from app.schemas.roadmap import RoadmapGenerateRequest, RoadmapProgressUpdate
from app.utils.jwt_handler import get_current_user
from app.utils.response import success_response

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


# ---------------------------------------------------------------------------
# POST /roadmap/generate
# ---------------------------------------------------------------------------


@router.post("/generate")
async def generate_roadmap(
    body: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a personalised week-by-week learning roadmap and persist it."""
    from app.ai.skill_gap import analyze_gap
    from app.ai.roadmap_generator import generate_roadmap as run_generator

    # Determine the skills the user needs for the target career
    gap_result = await analyze_gap(
        current_skills=[],
        target_career=body.target_career,
        db=db,
    )
    missing_skills = gap_result.get("missing_skills") or gap_result.get("priority_order", [])

    weeks_plan = run_generator(
        target_career=body.target_career,
        missing_skills=missing_skills,
        hours_per_week=body.hours_per_week,
        target_date=body.target_date,
    )

    record = LearningRoadmap(
        user_id=current_user.id,
        target_career=body.target_career,
        weeks_plan=weeks_plan,
        progress={},
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return success_response(
        data={
            "id": str(record.id),
            "target_career": record.target_career,
            "weeks_plan": record.weeks_plan,
            "progress": record.progress,
            "created_at": record.created_at.isoformat(),
        },
        message="Roadmap generated successfully",
    )


# ---------------------------------------------------------------------------
# GET /roadmap/me
# ---------------------------------------------------------------------------


@router.get("/me")
async def get_my_roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the current user's most recent learning roadmap."""
    result = await db.execute(
        select(LearningRoadmap)
        .where(LearningRoadmap.user_id == current_user.id)
        .order_by(LearningRoadmap.created_at.desc())
        .limit(1)
    )
    roadmap = result.scalar_one_or_none()

    if roadmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roadmap found. Generate one first.",
        )

    return success_response(
        data={
            "id": str(roadmap.id),
            "target_career": roadmap.target_career,
            "weeks_plan": roadmap.weeks_plan,
            "progress": roadmap.progress or {},
            "created_at": roadmap.created_at.isoformat(),
        },
        message="Roadmap retrieved",
    )


# ---------------------------------------------------------------------------
# PUT /roadmap/progress
# ---------------------------------------------------------------------------


@router.put("/progress")
async def update_roadmap_progress(
    body: RoadmapProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a specific week as complete (or incomplete) in the roadmap."""
    result = await db.execute(
        select(LearningRoadmap)
        .where(LearningRoadmap.user_id == current_user.id)
        .order_by(LearningRoadmap.created_at.desc())
        .limit(1)
    )
    roadmap = result.scalar_one_or_none()

    if roadmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roadmap found. Generate one first.",
        )

    progress = dict(roadmap.progress or {})
    progress[str(body.week_number)] = body.completed
    roadmap.progress = progress

    await db.commit()
    await db.refresh(roadmap)

    return success_response(
        data={"week_number": body.week_number, "completed": body.completed, "progress": progress},
        message="Progress updated",
    )
