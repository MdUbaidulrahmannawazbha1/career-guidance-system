"""
Skill-gap analysis module.

Compares the student's current skills against the canonical required-skills
list for a target career (stored in the ``career_skills_map`` table) and
uses sentence-transformer embeddings to measure semantic similarity so that
near-matches (e.g. "ML" vs "machine learning") are handled gracefully.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default learning resources per skill category (fallback when the DB row
# has no resources column value)
DEFAULT_RESOURCES: Dict[str, List[str]] = {
    "python": [
        "https://docs.python.org/3/tutorial/",
        "https://www.kaggle.com/learn/python",
    ],
    "machine learning": [
        "https://www.coursera.org/learn/machine-learning",
        "https://scikit-learn.org/stable/tutorial/",
    ],
    "data science": [
        "https://www.kaggle.com/learn",
        "https://www.datacamp.com",
    ],
    "aws": [
        "https://aws.amazon.com/training/",
        "https://acloudguru.com",
    ],
    "docker": [
        "https://docs.docker.com/get-started/",
        "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/",
    ],
    "default": [
        "https://www.coursera.org",
        "https://www.udemy.com",
        "https://www.youtube.com",
    ],
}

# Similarity threshold above which we consider a skill as "covered".
# 0.65 is chosen to be permissive enough to match semantic near-equivalents
# (e.g. "ML" ↔ "machine learning") while strict enough to reject unrelated
# skills.  Adjust via the SKILL_SIMILARITY_THRESHOLD env var if needed.
SIMILARITY_THRESHOLD: float = 0.65


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_embedding_model() -> Any:
    """Lazily load the sentence-transformer model."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
        from app.config import settings

        return SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
    except Exception as exc:  # pragma: no cover
        logger.warning("Could not load sentence-transformer model: %s", exc)
        return None


def _cosine_similarity(a: Any, b: Any) -> float:
    """Compute cosine similarity between two numpy vectors."""
    import numpy as np

    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return float(np.dot(a, b) / (a_norm * b_norm))


def _skill_covered(
    skill: str,
    current_embeddings: List[Any],
    required_embedding: Any,
    threshold: float,
) -> bool:
    """Return True if *any* current-skill embedding is similar enough."""
    for emb in current_embeddings:
        if _cosine_similarity(emb, required_embedding) >= threshold:
            return True
    return False


def _get_resources(skill: str, db_resources: Dict[str, Any] | None) -> List[str]:
    """Return learning resources for a skill, with DB data taking priority."""
    if db_resources:
        # DB resources is expected to be {skill_name: [url, ...]}
        skill_lower = skill.lower()
        for key, urls in db_resources.items():
            if key.lower() in skill_lower or skill_lower in key.lower():
                return urls if isinstance(urls, list) else [str(urls)]

    skill_lower = skill.lower()
    for key, urls in DEFAULT_RESOURCES.items():
        if key in skill_lower or skill_lower in key:
            return urls

    return DEFAULT_RESOURCES["default"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def analyze_gap(
    current_skills: List[str],
    target_career: str,
    db: Any,
) -> Dict[str, Any]:
    """Analyse the skill gap between the student's skills and a target career.

    Args:
        current_skills: List of skill strings the student already has.
        target_career:  Name of the target career (matched against career_skills_map).
        db:             An active SQLAlchemy async session.

    Returns:
        A dict with:
            ``have_skills``     – subset of required skills the student already has
            ``missing_skills``  – required skills the student still needs
            ``priority_order``  – missing_skills sorted by importance (order in DB)
            ``resources``       – {skill: [url, ...]} for each missing skill
    """
    from sqlalchemy import select
    from app.models.admin import CareerSkillsMap

    # ------------------------------------------------------------------
    # 1. Fetch required skills from the database
    # ------------------------------------------------------------------
    result = await db.execute(
        select(CareerSkillsMap).where(
            CareerSkillsMap.career_name.ilike(target_career)
        )
    )
    career_map = result.scalars().first()

    if career_map is None or not career_map.required_skills:
        logger.warning("No skill map found for career: %s", target_career)
        return {
            "have_skills": [],
            "missing_skills": [],
            "priority_order": [],
            "resources": {},
        }

    required_skills: List[str] = career_map.required_skills
    db_resources: Dict[str, Any] | None = career_map.resources

    # ------------------------------------------------------------------
    # 2. Use sentence-transformers to measure semantic similarity
    # ------------------------------------------------------------------
    model = _load_embedding_model()

    if model is not None and current_skills:
        current_embeddings = model.encode(current_skills, convert_to_numpy=True)
        required_embeddings = model.encode(required_skills, convert_to_numpy=True)
        have: List[str] = []
        missing: List[str] = []
        for req_skill, req_emb in zip(required_skills, required_embeddings):
            if _skill_covered(req_skill, current_embeddings, req_emb, SIMILARITY_THRESHOLD):
                have.append(req_skill)
            else:
                missing.append(req_skill)
    else:
        # Fallback: simple case-insensitive string matching
        current_lower = {s.lower() for s in current_skills}
        have = [s for s in required_skills if s.lower() in current_lower]
        missing = [s for s in required_skills if s.lower() not in current_lower]

    # ------------------------------------------------------------------
    # 3. Build resources map for missing skills
    # ------------------------------------------------------------------
    resources: Dict[str, List[str]] = {
        skill: _get_resources(skill, db_resources) for skill in missing
    }

    return {
        "have_skills": have,
        "missing_skills": missing,
        "priority_order": missing,   # order reflects DB priority ordering
        "resources": resources,
    }
