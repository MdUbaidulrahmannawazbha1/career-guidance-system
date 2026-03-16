"""
Assessment router.

Endpoints
---------
POST /assessment/career/start          – return 20 personality/interest questions
POST /assessment/career/submit         – score answers, save, return personality type
GET  /assessment/knowledge/start       – return 10 MCQs filtered by topic & difficulty
POST /assessment/knowledge/submit      – score, adapt difficulty, save result
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.assessment import CareerAssessment, KnowledgeAssessment
from app.models.user import User
from app.schemas.assessment import (
    CareerAssessmentResponse,
    CareerAssessmentSubmit,
    KnowledgeAssessmentResponse,
    KnowledgeAssessmentSubmit,
    KnowledgeAssessmentStartResponse,
)
from app.utils.jwt_handler import get_current_user
from app.utils.response import success_response

router = APIRouter(prefix="/assessment", tags=["assessment"])

# ---------------------------------------------------------------------------
# Built-in personality / interest questions (20 total)
# ---------------------------------------------------------------------------

_CAREER_QUESTIONS: List[Dict[str, Any]] = [
    {"id": "q1", "question": "I enjoy solving complex logical puzzles.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "analytical"},
    {"id": "q2", "question": "I like working in teams to accomplish goals.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "social"},
    {"id": "q3", "question": "I am interested in building and designing software applications.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "technical"},
    {"id": "q4", "question": "I enjoy analyzing data to find patterns and insights.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "analytical"},
    {"id": "q5", "question": "I am comfortable presenting ideas to large audiences.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "social"},
    {"id": "q6", "question": "I prefer structured environments with clear guidelines.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "organised"},
    {"id": "q7", "question": "I like creating visually appealing designs.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "creative"},
    {"id": "q8", "question": "I find security and ethical hacking topics fascinating.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "technical"},
    {"id": "q9", "question": "I enjoy managing projects and coordinating teams.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "leadership"},
    {"id": "q10", "question": "I am passionate about cloud infrastructure and DevOps.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "technical"},
    {"id": "q11", "question": "I prefer working independently over group settings.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "independent"},
    {"id": "q12", "question": "I am interested in business strategy and market analysis.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "business"},
    {"id": "q13", "question": "I enjoy learning new programming languages and frameworks.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "technical"},
    {"id": "q14", "question": "I like helping people solve their problems.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "social"},
    {"id": "q15", "question": "I am detail-oriented and notice small errors quickly.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "analytical"},
    {"id": "q16", "question": "I enjoy reading research papers and staying up to date with technology.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "technical"},
    {"id": "q17", "question": "I prefer creative problem-solving over rigid procedures.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "creative"},
    {"id": "q18", "question": "I am motivated by achieving measurable results.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "organised"},
    {"id": "q19", "question": "I am interested in AI and machine learning research.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "technical"},
    {"id": "q20", "question": "I enjoy mentoring and teaching others new concepts.", "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], "category": "social"},
]

# Scoring map: Strongly Agree=5, Agree=4, Neutral=3, Disagree=2, Strongly Disagree=1
_SCORE_MAP = {
    "strongly agree": 5,
    "agree": 4,
    "neutral": 3,
    "disagree": 2,
    "strongly disagree": 1,
}

_PERSONALITY_THRESHOLDS = [
    ("Investigative", ["analytical", "technical"]),
    ("Social", ["social", "leadership"]),
    ("Artistic", ["creative"]),
    ("Conventional", ["organised"]),
    ("Enterprising", ["business", "leadership"]),
]


def _score_career_answers(answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Score career assessment answers and return personality type + interest scores."""
    answer_map = {a["question_id"]: a["answer"] for a in answers}
    category_scores: Dict[str, float] = {}

    for q in _CAREER_QUESTIONS:
        raw_answer = answer_map.get(q["id"], "neutral")
        score = _SCORE_MAP.get(raw_answer.lower(), 3)
        cat = q["category"]
        category_scores[cat] = category_scores.get(cat, 0) + score

    # Determine personality type by dominant category group
    best_type = "Realistic"
    best_score = -1
    for ptype, cats in _PERSONALITY_THRESHOLDS:
        total = sum(category_scores.get(c, 0) for c in cats)
        if total > best_score:
            best_score = total
            best_type = ptype

    return {"personality_type": best_type, "interest_scores": category_scores}


# ---------------------------------------------------------------------------
# POST /assessment/career/start
# ---------------------------------------------------------------------------


@router.post("/career/start")
async def start_career_assessment(_: User = Depends(get_current_user)):
    """Return the 20 personality / interest questions."""
    return success_response(
        data={"questions": _CAREER_QUESTIONS, "total": len(_CAREER_QUESTIONS)},
        message="Career assessment questions loaded",
    )


# ---------------------------------------------------------------------------
# POST /assessment/career/submit
# ---------------------------------------------------------------------------


@router.post("/career/submit", response_model=CareerAssessmentResponse)
async def submit_career_assessment(
    body: CareerAssessmentSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Score submitted answers, persist assessment, return personality type."""
    answers_list = [a.model_dump() for a in body.answers]
    scoring = _score_career_answers(answers_list)

    record = CareerAssessment(
        user_id=current_user.id,
        answers=answers_list,
        personality_type=scoring["personality_type"],
        interest_scores=scoring["interest_scores"],
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


# ---------------------------------------------------------------------------
# GET /assessment/knowledge/start
# ---------------------------------------------------------------------------


@router.get("/knowledge/start", response_model=KnowledgeAssessmentStartResponse)
async def start_knowledge_assessment(
    topic: str = Query(..., description="Topic to be assessed"),
    difficulty: str = Query("medium", description="Difficulty level: easy, medium, hard"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch up to 10 MCQ questions for the given topic and difficulty."""
    from app.ai.knowledge_assessment import get_questions

    questions = await get_questions(topic=topic, difficulty=difficulty, db=db)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions found for topic '{topic}' with difficulty '{difficulty}'",
        )

    return KnowledgeAssessmentStartResponse(
        questions=questions,
        topic=topic,
        difficulty=difficulty,
    )


# ---------------------------------------------------------------------------
# POST /assessment/knowledge/submit
# ---------------------------------------------------------------------------


@router.post("/knowledge/submit", response_model=KnowledgeAssessmentResponse)
async def submit_knowledge_assessment(
    body: KnowledgeAssessmentSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Evaluate submitted answers, adapt difficulty, persist and return result."""
    from app.ai.knowledge_assessment import calculate_score, evaluate_answer

    evaluated: List[Dict[str, Any]] = []
    current_difficulty = body.difficulty

    for answer_item in body.answers:
        try:
            result = await evaluate_answer(
                question_id=answer_item.question_id,
                answer=answer_item.answer,
                current_difficulty=current_difficulty,
                db=db,
            )
            evaluated.append(result)
            current_difficulty = result.get("next_difficulty", current_difficulty)
        except ValueError:
            # Question not found – skip gracefully
            continue

    scoring = calculate_score(evaluated)

    record = KnowledgeAssessment(
        user_id=current_user.id,
        topic=body.topic,
        difficulty=body.difficulty,
        score=int(scoring["score"]),
        total_questions=scoring["total"],
        answers=[a.model_dump() for a in body.answers],
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return KnowledgeAssessmentResponse(
        id=record.id,
        topic=record.topic,
        difficulty=record.difficulty,
        score=record.score or 0,
        total_questions=record.total_questions or 0,
        level=scoring["level"],
        taken_at=record.taken_at,
    )
