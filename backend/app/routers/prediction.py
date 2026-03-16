"""
Prediction router.

Endpoints
---------
POST /predict/career              – run ML model, save, return top 5 careers
POST /predict/placement           – run XGBoost, return probability + weak areas
POST /predict/placement/simulate  – what-if simulation
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rate_limiter import limiter
from app.models.prediction import CareerPrediction, PlacementPrediction
from app.models.user import User
from app.schemas.prediction import (
    CareerPredictRequest,
    PlacementPredictRequest,
    SimulateRequest,
)
from app.utils.jwt_handler import get_current_user
from app.utils.response import success_response

router = APIRouter(prefix="/predict", tags=["prediction"])


def _build_features(body) -> dict:
    """Convert a prediction request body into the feature dict expected by AI modules."""
    return {
        "cgpa": body.cgpa,
        "num_skills": len(body.skills),
        "num_projects": body.projects,
        "internship": int(body.internship),
        "backlog": body.backlog,
        "personality_score": body.personality_score or 5.0,
        "interest_score": body.interest_score or 5.0,
    }


# ---------------------------------------------------------------------------
# POST /predict/career
# ---------------------------------------------------------------------------


@router.post("/career")
@limiter.limit("20/hour")
async def predict_career(
    request: Request,
    body: CareerPredictRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run the career recommendation ML model and return the top-5 careers."""
    from app.ai.career_recommender import predict_career as run_model

    features = _build_features(body)

    try:
        predictions = run_model(features)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    record = CareerPrediction(
        user_id=current_user.id,
        predicted_careers=[p["career"] for p in predictions],
        confidence_scores={p["career"]: p["confidence"] for p in predictions},
        input_features=features,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return success_response(
        data={
            "id": str(record.id),
            "predicted_careers": predictions,
            "created_at": record.created_at.isoformat(),
        },
        message="Career prediction complete",
    )


# ---------------------------------------------------------------------------
# POST /predict/placement
# ---------------------------------------------------------------------------


@router.post("/placement")
@limiter.limit("20/hour")
async def predict_placement(
    request: Request,
    body: PlacementPredictRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Predict campus placement probability and identify weak areas."""
    from app.ai.placement_predictor import predict_placement as run_model

    features = _build_features(body)

    try:
        result = run_model(features)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    record = PlacementPrediction(
        user_id=current_user.id,
        probability=result["probability"],
        weak_areas={"areas": result["weak_areas"], "tips": result["tips"]},
        input_features=features,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return success_response(
        data={
            "id": str(record.id),
            "probability": result["probability"],
            "weak_areas": result["weak_areas"],
            "tips": result["tips"],
            "created_at": record.created_at.isoformat(),
        },
        message="Placement prediction complete",
    )


# ---------------------------------------------------------------------------
# POST /predict/placement/simulate
# ---------------------------------------------------------------------------


@router.post("/placement/simulate")
async def simulate_placement(
    body: SimulateRequest,
    current_user: User = Depends(get_current_user),
):
    """What-if simulation: show the impact of improving skills/CGPA on placement."""
    from app.ai.placement_predictor import predict_placement, simulate_whatif

    features = _build_features(body)

    try:
        original = predict_placement(features)
        simulated = simulate_whatif(
            features,
            skill_increase=body.skill_increase,
            cgpa_increase=body.cgpa_increase,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return success_response(
        data={"original": original, "simulated": simulated},
        message="Simulation complete",
    )
