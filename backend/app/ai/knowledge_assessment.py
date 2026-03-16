"""
Knowledge assessment module.

Provides adaptive MCQ-based knowledge quizzes by querying the ``question_bank``
table, evaluating submitted answers and calculating a final score with a
proficiency level label.
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUESTIONS_PER_QUIZ: int = 10

# Difficulty progression rules
_DIFFICULTY_UP: Dict[str, str] = {
    "easy": "medium",
    "medium": "hard",
    "hard": "hard",
}
_DIFFICULTY_DOWN: Dict[str, str] = {
    "easy": "easy",
    "medium": "easy",
    "hard": "medium",
}

# Score thresholds for level labelling
_LEVEL_THRESHOLDS: List[Tuple[float, str]] = [
    (80.0, "Advanced"),
    (50.0, "Intermediate"),
    (0.0, "Beginner"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_dict(q: Any) -> Dict[str, Any]:
    """Convert a QuestionBank ORM row to a safe, client-facing dict."""
    return {
        "id": str(q.id),
        "topic": q.topic,
        "difficulty": q.difficulty.value if hasattr(q.difficulty, "value") else q.difficulty,
        "question": q.question,
        "options": q.options or [],
        # correct_answer is intentionally omitted from the public response
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_questions(
    topic: str,
    difficulty: str,
    db: Any,
) -> List[Dict[str, Any]]:
    """Fetch up to QUESTIONS_PER_QUIZ MCQ questions for the given topic/difficulty.

    Args:
        topic:      The subject area to filter on (case-insensitive).
        difficulty: One of ``easy``, ``medium`` or ``hard``.
        db:         An active SQLAlchemy async session.

    Returns:
        A list of question dicts (without the correct answer).
    """
    from sqlalchemy import select, func
    from app.models.admin import QuestionBank, Difficulty

    diff_enum = difficulty.lower()

    stmt = (
        select(QuestionBank)
        .where(QuestionBank.topic.ilike(f"%{topic}%"))
        .where(QuestionBank.difficulty == diff_enum)
        .order_by(func.random())
        .limit(QUESTIONS_PER_QUIZ)
    )

    result = await db.execute(stmt)
    questions = result.scalars().all()

    if not questions:
        logger.warning(
            "No questions found for topic='%s' difficulty='%s'; trying without difficulty filter.",
            topic, difficulty,
        )
        stmt_fallback = (
            select(QuestionBank)
            .where(QuestionBank.topic.ilike(f"%{topic}%"))
            .order_by(func.random())
            .limit(QUESTIONS_PER_QUIZ)
        )
        result = await db.execute(stmt_fallback)
        questions = result.scalars().all()

    return [_row_to_dict(q) for q in questions]


async def evaluate_answer(
    question_id: str,
    answer: str,
    current_difficulty: str,
    db: Any,
) -> Dict[str, Any]:
    """Check a submitted answer and recommend the next difficulty level.

    Args:
        question_id:         UUID string of the question being answered.
        answer:              The student's submitted answer string.
        current_difficulty:  The difficulty of the current question.
        db:                  An active SQLAlchemy async session.

    Returns:
        ``correct``           – bool
        ``correct_answer``    – the actual correct answer
        ``next_difficulty``   – recommended difficulty for the next question
    """
    import uuid as _uuid
    from sqlalchemy import select
    from app.models.admin import QuestionBank

    stmt = select(QuestionBank).where(QuestionBank.id == _uuid.UUID(question_id))
    result = await db.execute(stmt)
    question = result.scalars().first()

    if question is None:
        raise ValueError(f"Question not found: {question_id}")

    correct = answer.strip().lower() == question.correct_answer.strip().lower()

    if correct:
        next_difficulty = _DIFFICULTY_UP.get(current_difficulty.lower(), "medium")
    else:
        next_difficulty = _DIFFICULTY_DOWN.get(current_difficulty.lower(), "easy")

    return {
        "correct": correct,
        "correct_answer": question.correct_answer,
        "next_difficulty": next_difficulty,
    }


def calculate_score(answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall quiz score and assign a proficiency level.

    Args:
        answers: A list of dicts, each with at minimum a ``correct`` bool key
                 (as returned by :func:`evaluate_answer`).

    Returns:
        ``score``  – percentage score (0–100)
        ``level``  – Beginner / Intermediate / Advanced
        ``correct_count`` – number of correct answers
        ``total``         – total questions evaluated
    """
    if not answers:
        return {"score": 0.0, "level": "Beginner", "correct_count": 0, "total": 0}

    correct_count = sum(1 for a in answers if a.get("correct", False))
    total = len(answers)
    score = (correct_count / total) * 100

    level = "Beginner"
    for threshold, label in _LEVEL_THRESHOLDS:
        if score >= threshold:
            level = label
            break

    return {
        "score": round(score, 2),
        "level": level,
        "correct_count": correct_count,
        "total": total,
    }
