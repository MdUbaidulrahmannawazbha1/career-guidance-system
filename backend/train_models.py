"""
Model training script.

Generates synthetic training data and trains:
    1. career_model.pkl   – RandomForest for career classification
    2. label_encoder.pkl  – LabelEncoder for career labels
    3. scaler.pkl         – StandardScaler for feature normalisation
    4. placement_model.pkl – GradientBoosting binary classifier for placement

Run this script once before starting the API server:

    python train_models.py

The artefacts are saved to the directory specified by the ML_MODELS_DIR
setting (defaults to ``ml_models/``).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the backend/app package is importable when running from the repo root
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ---------------------------------------------------------------------------
# Career labels and features
# ---------------------------------------------------------------------------

CAREER_LABELS = [
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

FEATURE_NAMES = [
    "cgpa",            # 0–10
    "num_skills",      # 0–20
    "num_projects",    # 0–10
    "internship",      # 0 or 1
    "backlog",         # 0 or 1
    "personality_score",  # 1–10
    "interest_score",     # 1–10
]

N_SAMPLES_PER_CLASS = 200  # Sufficient for demonstration; increase for production use
RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)


# ---------------------------------------------------------------------------
# Synthetic data generators
# ---------------------------------------------------------------------------

def _make_career_samples() -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic (X, y) for career classification."""
    all_X: list[np.ndarray] = []
    all_y: list[int] = []

    # Rough heuristic profiles for each career
    profiles = {
        0: dict(cgpa=(7.5, 1.0), skills=(10, 3), projects=(4, 1), intern=0.7, interest=(7, 1.5)),  # SWE
        1: dict(cgpa=(8.0, 0.8), skills=(8, 2), projects=(5, 1), intern=0.6, interest=(8, 1.2)),   # DS
        2: dict(cgpa=(7.0, 1.0), skills=(9, 2), projects=(3, 1), intern=0.5, interest=(7, 1.5)),   # DevOps
        3: dict(cgpa=(8.2, 0.7), skills=(9, 2), projects=(5, 1), intern=0.65, interest=(8, 1.2)),  # ML
        4: dict(cgpa=(7.2, 1.0), skills=(8, 2), projects=(4, 1), intern=0.6, interest=(7, 1.5)),   # Web
        5: dict(cgpa=(7.5, 0.9), skills=(7, 2), projects=(3, 1), intern=0.5, interest=(7, 1.5)),   # Cyber
        6: dict(cgpa=(8.0, 0.8), skills=(9, 2), projects=(4, 1), intern=0.7, interest=(7.5, 1.2)), # Cloud
        7: dict(cgpa=(7.8, 0.9), skills=(6, 2), projects=(3, 1), intern=0.8, interest=(7, 1.5)),   # PM
        8: dict(cgpa=(7.5, 1.0), skills=(6, 2), projects=(3, 1), intern=0.7, interest=(7, 1.5)),   # BA
        9: dict(cgpa=(7.0, 1.0), skills=(6, 2), projects=(3, 1), intern=0.5, interest=(8, 1.2)),   # UX
    }

    for label_idx, p in profiles.items():
        n = N_SAMPLES_PER_CLASS
        cgpa = rng.normal(p["cgpa"][0], p["cgpa"][1], n).clip(4.0, 10.0)
        skills = rng.normal(p["skills"][0], p["skills"][1], n).clip(0, 20).astype(int)
        projects = rng.normal(p["projects"][0], p["projects"][1], n).clip(0, 10).astype(int)
        intern = (rng.random(n) < p["intern"]).astype(int)
        backlog = (rng.random(n) < 0.2).astype(int)
        personality = rng.normal(6.5, 1.5, n).clip(1, 10)
        interest = rng.normal(p["interest"][0], p["interest"][1], n).clip(1, 10)

        X = np.column_stack([cgpa, skills, projects, intern, backlog, personality, interest])
        y = np.full(n, label_idx, dtype=int)
        all_X.append(X)
        all_y.append(y)

    return np.vstack(all_X), np.concatenate(all_y)


def _make_placement_samples() -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic (X, y) for placement binary classification."""
    n = 2000
    cgpa = rng.normal(7.5, 1.2, n).clip(4.0, 10.0)
    skills = rng.normal(8, 3, n).clip(0, 20).astype(int)
    projects = rng.normal(3, 1.5, n).clip(0, 10).astype(int)
    intern = (rng.random(n) < 0.5).astype(int)
    backlog = (rng.random(n) < 0.25).astype(int)
    personality = rng.normal(6.5, 1.5, n).clip(1, 10)
    interest = rng.normal(6.5, 1.5, n).clip(1, 10)

    X = np.column_stack([cgpa, skills, projects, intern, backlog, personality, interest])

    # Heuristic label: higher CGPA, more skills/projects, internship → placed
    score = (
        (cgpa - 4) / 6 * 0.35
        + skills / 20 * 0.25
        + projects / 10 * 0.15
        + intern * 0.15
        + (1 - backlog) * 0.05
        + (personality - 1) / 9 * 0.025
        + (interest - 1) / 9 * 0.025
    )
    noise = rng.normal(0, 0.05, n)
    y = ((score + noise) > 0.5).astype(int)

    return X, y


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_career_model(output_dir: Path) -> None:
    print("Training career recommendation model …")
    X, y_raw = _make_career_samples()

    le = LabelEncoder()
    le.fit(CAREER_LABELS)
    y = le.transform([CAREER_LABELS[i] for i in y_raw])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=200, random_state=RANDOM_SEED, n_jobs=-1)
    model.fit(X_scaled, y)

    joblib.dump(model, output_dir / "career_model.pkl")
    joblib.dump(le, output_dir / "label_encoder.pkl")
    joblib.dump(scaler, output_dir / "scaler.pkl")
    print(f"  Saved: {output_dir / 'career_model.pkl'}")
    print(f"  Saved: {output_dir / 'label_encoder.pkl'}")
    print(f"  Saved: {output_dir / 'scaler.pkl'}")


def train_placement_model(output_dir: Path) -> None:
    print("Training placement prediction model …")
    X, y = _make_placement_samples()

    model = GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_SEED)
    model.fit(X, y)

    joblib.dump(model, output_dir / "placement_model.pkl")
    print(f"  Saved: {output_dir / 'placement_model.pkl'}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        from app.config import settings
        models_dir = Path(settings.ML_MODELS_DIR)
        if not models_dir.is_absolute():
            models_dir = _HERE / models_dir
    except Exception:
        models_dir = _HERE / "ml_models"

    models_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {models_dir}\n")

    train_career_model(models_dir)
    train_placement_model(models_dir)

    print("\nAll models trained successfully.")


if __name__ == "__main__":
    main()
