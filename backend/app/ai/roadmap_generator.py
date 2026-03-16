"""
Learning roadmap generator.

Distributes missing skills across weeks based on available hours per week
and the target completion date, producing a structured weekly plan with
topic, curated resources, a mini-project idea and estimated hours.
"""

from __future__ import annotations

import math
import logging
from datetime import date
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Static resource library
# ---------------------------------------------------------------------------

SKILL_RESOURCES: Dict[str, List[str]] = {
    "python": [
        "https://docs.python.org/3/tutorial/",
        "https://www.learnpython.org/",
        "https://www.kaggle.com/learn/python",
    ],
    "machine learning": [
        "https://www.coursera.org/learn/machine-learning",
        "https://scikit-learn.org/stable/tutorial/",
        "https://www.kaggle.com/learn/intro-to-machine-learning",
    ],
    "deep learning": [
        "https://www.deeplearning.ai/",
        "https://pytorch.org/tutorials/",
        "https://www.fast.ai/",
    ],
    "data science": [
        "https://www.kaggle.com/learn",
        "https://www.datacamp.com",
        "https://pandas.pydata.org/docs/getting_started/",
    ],
    "web development": [
        "https://developer.mozilla.org/en-US/docs/Learn",
        "https://www.freecodecamp.org/",
        "https://www.theodinproject.com/",
    ],
    "react": [
        "https://react.dev/learn",
        "https://www.epicreact.dev/",
        "https://beta.reactjs.org/",
    ],
    "node.js": [
        "https://nodejs.org/en/docs/",
        "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/",
    ],
    "aws": [
        "https://aws.amazon.com/training/",
        "https://acloudguru.com",
        "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/",
    ],
    "docker": [
        "https://docs.docker.com/get-started/",
        "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/",
    ],
    "kubernetes": [
        "https://kubernetes.io/docs/tutorials/",
        "https://www.cncf.io/certification/ckad/",
    ],
    "sql": [
        "https://www.w3schools.com/sql/",
        "https://mode.com/sql-tutorial/",
        "https://sqlzoo.net/",
    ],
    "cybersecurity": [
        "https://www.cybrary.it/",
        "https://tryhackme.com/",
        "https://www.hackthebox.com/",
    ],
    "default": [
        "https://www.coursera.org",
        "https://www.udemy.com",
        "https://www.youtube.com",
        "https://www.geeksforgeeks.org",
    ],
}

SKILL_MINI_PROJECTS: Dict[str, str] = {
    "python": "Build a CLI tool or automation script using Python.",
    "machine learning": "Train a classification model on a Kaggle dataset and evaluate metrics.",
    "deep learning": "Build an image classifier using CNNs with PyTorch or TensorFlow.",
    "data science": "Perform EDA and generate insights on a public dataset.",
    "web development": "Create a responsive portfolio website with HTML, CSS and JavaScript.",
    "react": "Build a React to-do app with hooks and local state management.",
    "node.js": "Develop a REST API with Express.js and connect it to a database.",
    "aws": "Deploy a static website to S3 and set up a CloudFront distribution.",
    "docker": "Containerise an existing application and write a docker-compose file.",
    "kubernetes": "Deploy a simple microservice cluster on minikube.",
    "sql": "Design and query a relational database schema for an e-commerce store.",
    "cybersecurity": "Complete a beginner CTF challenge on TryHackMe.",
    "default": "Build a small project to demonstrate your understanding of the skill.",
}

# Estimated learning hours per skill level (introductory)
DEFAULT_HOURS_PER_SKILL: int = 8


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_resources(skill: str) -> List[str]:
    skill_lower = skill.lower()
    for key, urls in SKILL_RESOURCES.items():
        if key in skill_lower or skill_lower in key:
            return urls
    return SKILL_RESOURCES["default"]


def _get_mini_project(skill: str) -> str:
    skill_lower = skill.lower()
    for key, project in SKILL_MINI_PROJECTS.items():
        if key in skill_lower or skill_lower in key:
            return project
    return SKILL_MINI_PROJECTS["default"]


def _weeks_available(hours_per_week: int, target_date: Optional[date]) -> int:
    """Return the number of weeks until the target date (min 1)."""
    if target_date is None:
        return 52  # default to ~1 year
    today = date.today()
    delta_days = (target_date - today).days
    if delta_days <= 0:
        logger.warning(
            "target_date %s is in the past or today; defaulting to 1 week.", target_date
        )
        return 1
    return max(1, delta_days // 7)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_roadmap(
    target_career: str,
    missing_skills: List[str],
    hours_per_week: int,
    target_date: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Generate a week-by-week learning roadmap.

    Args:
        target_career:  The career goal (used in week descriptions).
        missing_skills: Ordered list of skills to learn.
        hours_per_week: Number of hours the student can dedicate per week.
        target_date:    Desired completion date (optional).

    Returns:
        A list of week dicts, each with:
            ``week``             – week number (1-indexed)
            ``topic``            – primary skill to study that week
            ``skills_covered``   – list of skills grouped into this week
            ``resources``        – list of resource URLs
            ``mini_project``     – suggested mini-project description
            ``estimated_hours``  – estimated study hours for the week
    """
    if not missing_skills:
        return []

    if hours_per_week <= 0:
        hours_per_week = 10  # sensible default

    total_weeks = _weeks_available(hours_per_week, target_date)
    total_hours = total_weeks * hours_per_week  # noqa: F841

    # Assign approximate hours per skill
    hours_per_skill = max(DEFAULT_HOURS_PER_SKILL, hours_per_week // 2)
    # How many weeks per skill?
    weeks_per_skill = max(1, math.ceil(hours_per_skill / hours_per_week))

    roadmap: List[Dict[str, Any]] = []
    week_number = 1

    for skill in missing_skills:
        if week_number > total_weeks:
            break

        skill_weeks = min(weeks_per_skill, total_weeks - week_number + 1)
        week_hours = hours_per_week
        resources = _get_resources(skill)
        mini_project = _get_mini_project(skill)

        # First week for this skill
        roadmap.append(
            {
                "week": week_number,
                "topic": skill,
                "skills_covered": [skill],
                "resources": resources,
                "mini_project": mini_project if skill_weeks == 1 else f"Progress checkpoint: practice {skill} concepts.",
                "estimated_hours": week_hours,
            }
        )
        week_number += 1

        # Additional weeks (if the skill requires more than 1 week)
        for extra in range(1, skill_weeks):
            if week_number > total_weeks:
                break
            is_last = extra == skill_weeks - 1
            roadmap.append(
                {
                    "week": week_number,
                    "topic": f"{skill} (continued)",
                    "skills_covered": [skill],
                    "resources": resources,
                    "mini_project": mini_project if is_last else f"Build incrementally on your {skill} knowledge.",
                    "estimated_hours": week_hours,
                }
            )
            week_number += 1

    return roadmap
