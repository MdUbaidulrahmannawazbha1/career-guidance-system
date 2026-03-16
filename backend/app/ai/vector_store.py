"""
Vector store module (ChromaDB).

Provides helpers for persisting and querying resume/job embeddings so that
students can discover similar peer profiles and matching career opportunities.

Collections used:
    resume_embeddings  – one document per user, metadata contains user_id
    career_embeddings  – one document per career, metadata contains career label
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------

_chroma_client: Any = None


def _get_client() -> Any:
    """Return a (cached) ChromaDB HTTP client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb  # type: ignore[import-untyped]
        from app.config import settings

        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
    return _chroma_client


def _get_collection(name: str) -> Any:
    client = _get_client()
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def _embed_skills(skills: List[str]) -> List[float]:
    """Return a single embedding vector for a list of skills."""
    from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
    from app.config import settings
    import numpy as np

    model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
    # Embed skills as a single joined text; use an empty-skill placeholder so
    # the embedding is not generated from a semantically misleading term.
    skill_text = " ".join(skills) if skills else ""
    if not skill_text:
        # Return a zero vector of the model's embedding dimension
        dim = model.get_sentence_embedding_dimension() or 384
        return [0.0] * dim
    embedding = model.encode(skill_text, convert_to_numpy=True)
    return embedding.tolist()


# ---------------------------------------------------------------------------
# Resume embeddings
# ---------------------------------------------------------------------------

def add_resume_embedding(user_id: str, skills: List[str]) -> None:
    """Upsert a resume embedding for the given user.

    Args:
        user_id: The user's UUID string (used as the document ID).
        skills:  List of skill strings extracted from the user's resume.
    """
    collection = _get_collection(_collection_name("resume"))
    embedding = _embed_skills(skills)
    skills_str = ", ".join(skills)
    collection.upsert(
        ids=[user_id],
        embeddings=[embedding],
        documents=[skills_str],
        metadatas=[{"user_id": user_id, "skills": skills_str}],
    )
    logger.info("Upserted resume embedding for user_id=%s", user_id)


def search_similar_profiles(
    skills: List[str],
    n_results: int = 5,
) -> List[Dict[str, Any]]:
    """Find users with similar skill profiles.

    Args:
        skills:    The query user's skills.
        n_results: Maximum number of similar profiles to return.

    Returns:
        A list of dicts with ``user_id``, ``skills`` and ``distance`` keys.
    """
    collection = _get_collection(_collection_name("resume"))
    embedding = _embed_skills(skills)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["metadatas", "distances"],
    )

    profiles: List[Dict[str, Any]] = []
    if results and results.get("ids"):
        for i, uid in enumerate(results["ids"][0]):
            meta = (results.get("metadatas") or [[]])[0][i] if results.get("metadatas") else {}
            dist = (results.get("distances") or [[]])[0][i] if results.get("distances") else None
            profiles.append(
                {
                    "user_id": uid,
                    "skills": meta.get("skills", ""),
                    "distance": dist,
                }
            )
    return profiles


# ---------------------------------------------------------------------------
# Job / career embeddings
# ---------------------------------------------------------------------------

def add_job_embedding(career: str, skills: List[str]) -> None:
    """Upsert a career-skills embedding into the career collection.

    Args:
        career: Career label string (used as the document ID).
        skills: Required skill strings for the career.
    """
    collection = _get_collection(_collection_name("career"))
    embedding = _embed_skills(skills)
    skills_str = ", ".join(skills)
    collection.upsert(
        ids=[career],
        embeddings=[embedding],
        documents=[skills_str],
        metadatas=[{"career": career, "skills": skills_str}],
    )
    logger.info("Upserted job embedding for career=%s", career)


def search_matching_jobs(
    user_skills: List[str],
    n_results: int = 5,
) -> List[Dict[str, Any]]:
    """Find careers that best match the user's skills.

    Args:
        user_skills: The user's current skills.
        n_results:   Maximum number of matching careers to return.

    Returns:
        A list of dicts with ``career``, ``required_skills`` and ``distance``.
    """
    collection = _get_collection(_collection_name("career"))
    embedding = _embed_skills(user_skills)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["metadatas", "distances"],
    )

    careers: List[Dict[str, Any]] = []
    if results and results.get("ids"):
        for i, cid in enumerate(results["ids"][0]):
            meta = (results.get("metadatas") or [[]])[0][i] if results.get("metadatas") else {}
            dist = (results.get("distances") or [[]])[0][i] if results.get("distances") else None
            careers.append(
                {
                    "career": cid,
                    "required_skills": meta.get("skills", ""),
                    "distance": dist,
                }
            )
    return careers


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _collection_name(kind: str) -> str:
    """Return the configured ChromaDB collection name for *kind*."""
    from app.config import settings

    if kind == "resume":
        return settings.CHROMA_COLLECTION_RESUMES
    if kind == "career":
        return settings.CHROMA_COLLECTION_CAREERS
    raise ValueError(f"Unknown collection kind: {kind}")
