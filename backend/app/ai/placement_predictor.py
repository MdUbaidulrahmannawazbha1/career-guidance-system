"""
Placement prediction module.

Loads a pre-trained binary classifier and uses it to predict the probability
of campus placement for a student.  Also exposes a what-if simulator so
students can see the impact of improving their skills or CGPA.

Expected model artefact (relative to the configured ML_MODELS_DIR):
    placement_model.pkl – a fitted sklearn-compatible binary classifier
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feature metadata
# ---------------------------------------------------------------------------

FEATURE_ORDER: List[str] = [
    "cgpa",
    "num_skills",
    "num_projects",
    "internship",
    "backlog",
    "personality_score",
    "interest_score",
]

# Thresholds used to surface weak areas and personalised tips
_THRESHOLDS: Dict[str, float] = {
    "cgpa": 7.0,
    "num_skills": 5.0,
    "num_projects": 2.0,
    "personality_score": 6.0,
    "interest_score": 6.0,
}

_TIPS_MAP: Dict[str, str] = {
    "cgpa": "Improve your academic CGPA – aim for at least 7.0 to stay competitive.",
    "num_skills": "Expand your technical skill set by learning in-demand technologies.",
    "num_projects": "Build more hands-on projects to demonstrate practical ability.",
    "internship": "Complete at least one internship to gain real-world experience.",
    "backlog": "Clear any pending backlogs – they significantly impact shortlisting.",
    "personality_score": "Work on soft skills: communication, teamwork, and leadership.",
    "interest_score": "Develop a clear career interest and align your preparation accordingly.",
}

# Populated by load_model()
_model: Any = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _models_dir() -> Path:
    from app.config import settings

    base = Path(settings.ML_MODELS_DIR)
    if not base.is_absolute():
        # Resolve relative to the backend root (parents[2] from app/ai/<file>.py)
        base = Path(__file__).resolve().parents[2] / base
    return base


def _feature_vector(features: Dict[str, Any]) -> np.ndarray:
    return np.array([[float(features.get(key, 0)) for key in FEATURE_ORDER]])


def _derive_weak_areas_and_tips(
    features: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
    """Return (weak_areas, tips) lists based on threshold comparisons."""
    weak: List[str] = []
    tips: List[str] = []

    for field, threshold in _THRESHOLDS.items():
        if float(features.get(field, 0)) < threshold:
            weak.append(field)
            tips.append(_TIPS_MAP[field])

    if not int(features.get("internship", 0)):
        weak.append("internship")
        tips.append(_TIPS_MAP["internship"])

    if int(features.get("backlog", 0)):
        weak.append("backlog")
        tips.append(_TIPS_MAP["backlog"])

    return weak, tips


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_model() -> None:
    """Load the placement model artefact from disk."""
    global _model

    models_dir = _models_dir()
    model_path = models_dir / "placement_model.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Placement model artefact not found: {model_path}. "
            "Run train_models.py to generate the required .pkl file."
        )

    _model = joblib.load(model_path)
    logger.info("Placement predictor model loaded successfully.")


def predict_placement(features: Dict[str, Any]) -> Dict[str, Any]:
    """Predict placement probability and surface weak areas with tips.

    Args:
        features: Dict with keys matching FEATURE_ORDER.

    Returns:
        ``probability``  – placement probability as a percentage (0–100)
        ``weak_areas``   – list of feature names below recommended thresholds
        ``tips``         – list of actionable improvement suggestions
    """
    global _model

    if _model is None:
        load_model()

    vec = _feature_vector(features)

    if hasattr(_model, "predict_proba"):
        # Probability of positive class (index 1 = placed)
        proba = float(_model.predict_proba(vec)[0][1]) * 100
    else:
        pred = int(_model.predict(vec)[0])
        proba = 100.0 if pred == 1 else 0.0

    weak_areas, tips = _derive_weak_areas_and_tips(features)

    return {
        "probability": round(proba, 2),
        "weak_areas": weak_areas,
        "tips": tips,
    }


def simulate_whatif(
    features: Dict[str, Any],
    skill_increase: float = 0.0,
    cgpa_increase: float = 0.0,
) -> Dict[str, Any]:
    """Return the predicted placement probability after hypothetical improvements.

    Args:
        features:       Original feature dict.
        skill_increase: Number of additional skills to add to num_skills.
        cgpa_increase:  CGPA points to add to the current CGPA.

    Returns:
        Same structure as :func:`predict_placement` but for the improved profile.
    """
    improved = dict(features)
    improved["num_skills"] = float(improved.get("num_skills", 0)) + skill_increase
    improved["cgpa"] = float(improved.get("cgpa", 0)) + cgpa_increase

    return predict_placement(improved)
