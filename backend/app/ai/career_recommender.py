"""
Career recommendation module.

Loads a pre-trained multi-class classifier from disk and returns the top-5
predicted careers together with their confidence percentages.

Expected model artefacts (relative to the configured ML_MODELS_DIR):
    career_model.pkl   – a fitted sklearn-compatible classifier
    label_encoder.pkl  – a fitted LabelEncoder for the career labels
    scaler.pkl         – a fitted StandardScaler for the input features
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CAREER_LABELS: List[str] = [
    "Software Engineer",
    "Data Scientist",
    "DevOps Engineer",
    "ML Engineer",
    "Web Developer",
    "Cybersecurity Analyst",
    "Cloud Architect",
    "Product Manager",
    "Business Analyst",
    "UI/UX Designer",
]

FEATURE_ORDER: List[str] = [
    "cgpa",
    "num_skills",
    "num_projects",
    "internship",
    "backlog",
    "personality_score",
    "interest_score",
]

# Populated by load_model()
_model: Any = None
_label_encoder: Any = None
_scaler: Any = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _models_dir() -> Path:
    """Return the absolute path to the ML models directory."""
    from app.config import settings

    base = Path(settings.ML_MODELS_DIR)
    if not base.is_absolute():
        # Resolve relative to the backend root (parents[2] from app/ai/<file>.py)
        base = Path(__file__).resolve().parents[2] / base
    return base


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_model() -> None:
    """Load career model artefacts from disk into module-level globals."""
    global _model, _label_encoder, _scaler

    models_dir = _models_dir()
    model_path = models_dir / "career_model.pkl"
    le_path = models_dir / "label_encoder.pkl"
    scaler_path = models_dir / "scaler.pkl"

    for path in (model_path, le_path, scaler_path):
        if not path.exists():
            raise FileNotFoundError(
                f"Career model artefact not found: {path}. "
                "Run train_models.py to generate the required .pkl files."
            )

    _model = joblib.load(model_path)
    _label_encoder = joblib.load(le_path)
    _scaler = joblib.load(scaler_path)
    logger.info("Career recommender model loaded successfully.")


def predict_career(features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return top-5 career recommendations with confidence percentages.

    Args:
        features: A dict with keys matching FEATURE_ORDER.  Missing numeric
                  keys default to 0.

    Returns:
        A list of up to 5 dicts, each containing:
            ``career``     – career label string
            ``confidence`` – confidence as a percentage float (0–100)
    """
    global _model, _label_encoder, _scaler

    if _model is None:
        load_model()

    # Build the feature vector in the correct order
    feature_vector = np.array(
        [[float(features.get(key, 0)) for key in FEATURE_ORDER]]
    )

    # Scale features
    if _scaler is not None:
        feature_vector = _scaler.transform(feature_vector)

    # Obtain class probabilities
    if hasattr(_model, "predict_proba"):
        proba = _model.predict_proba(feature_vector)[0]
    else:
        # Fallback for models without predict_proba: one-hot encode prediction
        pred_idx = int(_model.predict(feature_vector)[0])
        proba = np.zeros(len(_label_encoder.classes_))
        proba[pred_idx] = 1.0

    # Map indices → labels
    classes = _label_encoder.classes_
    ranked = sorted(
        zip(classes, proba.tolist()), key=lambda x: x[1], reverse=True
    )

    return [
        {"career": str(career), "confidence": round(conf * 100, 2)}
        for career, conf in ranked[:5]
    ]
