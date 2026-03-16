"""
Analysis router.

Endpoints
---------
POST /analyze/resume      – upload PDF, run analyzer, save, return results
POST /analyze/skill-gap   – compare skills vs target career, return gap
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rate_limiter import limiter
from app.models.analysis import Resume, SkillGapAnalysis
from app.models.user import User
from app.schemas.analysis import ResumeAnalysisResponse, SkillGapRequest, SkillGapResponse
from app.utils.file_handler import save_upload, validate_pdf
from app.utils.jwt_handler import get_current_user
from app.utils.response import success_response

router = APIRouter(prefix="/analyze", tags=["analysis"])


# ---------------------------------------------------------------------------
# POST /analyze/resume
# ---------------------------------------------------------------------------


@router.post("/resume")
@limiter.limit("10/hour")
async def analyze_resume(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF résumé, analyse it and persist the results."""
    from app.ai.resume_analyzer import analyze_resume as run_resume_analyzer

    await validate_pdf(file)
    file_path = await save_upload(file, str(current_user.id))

    try:
        analysis = run_resume_analyzer(file_path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume analysis failed: {exc}",
        ) from exc

    record = Resume(
        user_id=current_user.id,
        file_path=file_path,
        extracted_skills=analysis.get("extracted_skills", []),
        extracted_education=analysis.get("education", []),
        extracted_experience=analysis.get("experience", []),
        score=analysis.get("score", 0),
        suggestions=analysis.get("suggestions", []),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return success_response(
        data={
            "id": str(record.id),
            "file_path": record.file_path,
            "extracted_skills": record.extracted_skills,
            "extracted_education": record.extracted_education,
            "extracted_experience": record.extracted_experience,
            "score": record.score,
            "suggestions": record.suggestions,
            "uploaded_at": record.uploaded_at.isoformat(),
        },
        message="Resume analyzed successfully",
    )


# ---------------------------------------------------------------------------
# POST /analyze/skill-gap
# ---------------------------------------------------------------------------


@router.post("/skill-gap")
async def analyze_skill_gap(
    body: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare the user's current skills against a target career and return the gap."""
    from app.ai.skill_gap import analyze_gap

    gap = await analyze_gap(
        current_skills=body.current_skills,
        target_career=body.target_career,
        db=db,
    )

    record = SkillGapAnalysis(
        user_id=current_user.id,
        target_career=body.target_career,
        current_skills=body.current_skills,
        missing_skills=gap.get("missing_skills", []),
        resources=gap.get("resources", {}),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return success_response(
        data={
            "id": str(record.id),
            "target_career": record.target_career,
            "have_skills": gap.get("have_skills", []),
            "missing_skills": gap.get("missing_skills", []),
            "priority_order": gap.get("priority_order", []),
            "resources": gap.get("resources", {}),
            "created_at": record.created_at.isoformat(),
        },
        message="Skill gap analysis complete",
    )
