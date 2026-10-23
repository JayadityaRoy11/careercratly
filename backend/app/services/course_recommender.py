from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.providers.courses import get_course_provider


def recommend_courses(missing_skills: list[str]) -> dict[str, Any]:
    provider = get_course_provider()
    unique: list[str] = []
    seen: set[str] = set()
    for skill in missing_skills:
        key = skill.strip()
        if not key or key.lower() in seen:
            continue
        seen.add(key.lower())
        unique.append(key)

    recommendations = []
    for skill in unique:
        courses = provider.recommend(skill, limit=settings.max_courses_per_skill)
        recommendations.append({"skill": skill, "courses": courses})
    return {"recommendations": recommendations}
