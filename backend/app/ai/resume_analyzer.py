"""
Resume analysis module.

Parses a PDF resume, runs Named-Entity Recognition with spaCy, scores the
resume on several quality dimensions and returns structured information that
can be stored and displayed to the student.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Known skills vocabulary (extend as needed)
# ---------------------------------------------------------------------------

KNOWN_SKILLS: List[str] = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
    "rust", "kotlin", "swift", "r", "scala", "ruby", "php", "dart",
    # Web
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "express",
    "django", "flask", "fastapi", "spring", "spring boot", "asp.net",
    # Data / ML
    "machine learning", "deep learning", "data science", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "keras", "nlp",
    "natural language processing", "computer vision",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "terraform", "ansible", "linux", "git", "github",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "sqlite", "oracle",
    # Other
    "agile", "scrum", "rest api", "graphql", "microservices", "blockchain",
    "cybersecurity", "figma", "ui/ux", "product management",
]

ACTION_VERBS: List[str] = [
    "developed", "designed", "built", "created", "implemented", "led",
    "managed", "improved", "optimized", "achieved", "delivered", "launched",
    "collaborated", "architected", "engineered", "automated", "reduced",
    "increased", "deployed", "integrated", "mentored", "analysed", "analyzed",
    "researched", "coordinated",
]

CERT_KEYWORDS: List[str] = [
    "certified", "certification", "certificate", "aws certified",
    "google cloud", "microsoft certified", "comptia", "cisco", "pmp",
    "scrum master", "coursera", "udemy", "nptel", "edx",
]

EDUCATION_KEYWORDS: List[str] = [
    "b.tech", "b.e", "bachelor", "m.tech", "master", "mba", "phd", "bsc",
    "msc", "engineering", "university", "college", "institute", "cgpa",
    "gpa", "10th", "12th", "ssc", "hsc", "diploma",
]

EXPERIENCE_KEYWORDS: List[str] = [
    "internship", "intern", "experience", "work experience", "employment",
    "company", "organisation", "organization", "role", "position",
    "responsibilities",
]

CONTACT_PATTERNS: List[re.Pattern] = [
    re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,4}(?:\.[a-z]{2})?(?=\s|$)", re.IGNORECASE),  # email
    re.compile(r"(?<!\d)(\+91[-\s]?)?[6-9]\d{9}(?!\d)"),  # Indian phone (word-boundary via lookbehind/ahead)
    re.compile(r"linkedin\.com/in/[\w-]+", re.IGNORECASE),
    re.compile(r"github\.com/[\w-]+", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def _extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF file using PyPDF2."""
    try:
        import PyPDF2  # type: ignore[import-untyped]

        text_parts: List[str] = []
        with open(file_path, "rb") as fh:
            reader = PyPDF2.PdfReader(fh)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:  # pragma: no cover
        logger.error("PDF text extraction failed for %s: %s", file_path, exc)
        return ""


def _extract_text(file_path: str) -> str:
    """Dispatch to the appropriate extractor based on file extension."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _extract_text_from_pdf(file_path)
    if ext in {".doc", ".docx"}:
        try:
            import docx  # type: ignore[import-untyped]

            doc = docx.Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:  # pragma: no cover
            logger.error("DOCX extraction failed for %s: %s", file_path, exc)
            return ""
    if ext == ".txt":
        with open(file_path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    raise ValueError(f"Unsupported file type: {ext}")


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _extract_skills(text: str) -> List[str]:
    lower = text.lower()
    return [skill for skill in KNOWN_SKILLS if skill in lower]


def _extract_education(text: str, ner_doc: Any) -> List[str]:
    """Combine keyword matching with spaCy ORG/GPE entities as fallback."""
    lower = text.lower()
    found: List[str] = []

    # Keyword-based line extraction
    for line in text.splitlines():
        if any(kw in line.lower() for kw in EDUCATION_KEYWORDS):
            stripped = line.strip()
            if stripped:
                found.append(stripped)

    # spaCy entities
    if ner_doc is not None:
        for ent in ner_doc.ents:
            if ent.label_ in {"ORG", "GPE"} and any(
                kw in lower for kw in ("university", "college", "institute")
            ):
                if ent.text not in found:
                    found.append(ent.text)

    return list(dict.fromkeys(found))  # preserve order, remove duplicates


def _extract_experience(text: str) -> List[str]:
    found: List[str] = []
    for line in text.splitlines():
        if any(kw in line.lower() for kw in EXPERIENCE_KEYWORDS):
            stripped = line.strip()
            if stripped:
                found.append(stripped)
    return list(dict.fromkeys(found))


def _extract_certifications(text: str) -> List[str]:
    found: List[str] = []
    for line in text.splitlines():
        if any(kw in line.lower() for kw in CERT_KEYWORDS):
            stripped = line.strip()
            if stripped:
                found.append(stripped)
    return list(dict.fromkeys(found))


def _has_contact_info(text: str) -> bool:
    return any(pat.search(text) for pat in CONTACT_PATTERNS)


def _has_quantified_achievements(text: str) -> bool:
    # Look for numbers combined with % or words that imply metrics
    return bool(re.search(r"\d+\s*(%|percent|x\b|times|users|customers|ms\b)", text, re.IGNORECASE))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_resume(
    text: str,
    skills: List[str],
    experience: List[str],
    certifications: List[str],
) -> Dict[str, Any]:
    """Score the resume across 6 dimensions (total 100 pts)."""
    lower = text.lower()

    # 1. Skills section (0-25 pts)
    skills_score = min(len(skills) * 2.5, 25)

    # 2. Projects (0-20 pts): look for a projects section or mentions
    project_mentions = len(re.findall(r"\bproject\b", lower))
    projects_score = min(project_mentions * 4, 20)

    # 3. Experience (0-20 pts)
    experience_score = min(len(experience) * 4, 20)

    # 4. Action verbs (0-15 pts)
    verb_count = sum(1 for v in ACTION_VERBS if v in lower)
    verbs_score = min(verb_count * 1.5, 15)

    # 5. Quantified achievements (0-10 pts)
    quant_score = 10 if _has_quantified_achievements(text) else 0

    # 6. Contact info (0-10 pts)
    contact_score = 10 if _has_contact_info(text) else 0

    total = skills_score + projects_score + experience_score + verbs_score + quant_score + contact_score
    total = min(round(total), 100)

    return {
        "total": total,
        "breakdown": {
            "skills": round(skills_score),
            "projects": round(projects_score),
            "experience": round(experience_score),
            "action_verbs": round(verbs_score),
            "quantified_achievements": round(quant_score),
            "contact_info": round(contact_score),
        },
    }


def _generate_suggestions(score_details: Dict[str, Any], skills: List[str]) -> List[str]:
    suggestions: List[str] = []
    bd = score_details["breakdown"]

    if bd["skills"] < 15:
        suggestions.append("Add a dedicated 'Skills' section listing 8–10 relevant technologies.")
    if bd["projects"] < 12:
        suggestions.append("Include at least 3 projects with problem statement, tech stack, and outcome.")
    if bd["experience"] < 12:
        suggestions.append("Detail your internship/work experience with role, company, and duration.")
    if bd["action_verbs"] < 10:
        suggestions.append("Use strong action verbs (e.g., 'Developed', 'Led', 'Optimised') to describe accomplishments.")
    if bd["quantified_achievements"] == 0:
        suggestions.append("Quantify your achievements (e.g., 'Reduced load time by 40%', 'Onboarded 200+ users').")
    if bd["contact_info"] == 0:
        suggestions.append("Ensure your email, phone number, and LinkedIn/GitHub URLs are clearly visible.")
    if len(skills) < 5:
        suggestions.append("Broaden your skill set – aim for at least 5 in-demand technologies.")

    return suggestions


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_resume(file_path: str) -> Dict[str, Any]:
    """Analyse a resume file and return structured information.

    Args:
        file_path: Absolute or relative path to the resume file
                   (PDF, DOCX or TXT).

    Returns:
        A dict with keys:
            ``extracted_skills``  – list of recognised skill strings
            ``education``         – list of education-related text lines
            ``experience``        – list of experience-related text lines
            ``certifications``    – list of certification-related text lines
            ``score``             – overall quality score (0–100)
            ``score_breakdown``   – per-dimension scores
            ``suggestions``       – list of improvement recommendations
    """
    text = _extract_text(file_path)

    # Run spaCy NER
    ner_doc = None
    try:
        import spacy  # type: ignore[import-untyped]

        from app.config import settings

        nlp = spacy.load(settings.SPACY_MODEL)
        ner_doc = nlp(text[:100_000])  # spaCy cap
    except Exception as exc:  # pragma: no cover
        logger.warning("spaCy NER unavailable: %s", exc)

    skills = _extract_skills(text)
    education = _extract_education(text, ner_doc)
    experience = _extract_experience(text)
    certifications = _extract_certifications(text)
    score_details = _score_resume(text, skills, experience, certifications)
    suggestions = _generate_suggestions(score_details, skills)

    return {
        "extracted_skills": skills,
        "education": education,
        "experience": experience,
        "certifications": certifications,
        "score": score_details["total"],
        "score_breakdown": score_details["breakdown"],
        "suggestions": suggestions,
    }
