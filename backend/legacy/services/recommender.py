"""Course recommendation backends.

Set COURSE_RECOMMENDER=static (default) to query the local courses table.
Swap later for a live catalog (Coursera API) or LLM-generated suggestions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.course import Course, CourseLevel

LEVEL_RANK = {
    CourseLevel.BEGINNER: 0,
    CourseLevel.INTERMEDIATE: 1,
    CourseLevel.ADVANCED: 2,
}


class CourseRecommender(ABC):
    name: str

    @abstractmethod
    async def recommend(
        self,
        session: AsyncSession,
        missing_skills: list[str],
        *,
        max_per_skill: int = 3,
    ) -> dict[str, list[Course]]:
        """Return up to `max_per_skill` courses for each missing skill name."""


class StaticTableRecommender(CourseRecommender):
    """Match missing skills to rows in the local `courses` table."""

    name = "static"

    async def recommend(
        self,
        session: AsyncSession,
        missing_skills: list[str],
        *,
        max_per_skill: int = 3,
    ) -> dict[str, list[Course]]:
        grouped: dict[str, list[Course]] = {skill: [] for skill in missing_skills}
        if not missing_skills:
            return grouped

        wanted = {skill.lower(): skill for skill in missing_skills}
        result = await session.execute(
            select(Course).where(Course.skill_tag.in_(list(wanted.values())))
        )
        by_tag: dict[str, list[Course]] = defaultdict(list)
        for course in result.scalars().all():
            canonical = wanted.get(course.skill_tag.lower())
            if canonical is None:
                continue
            by_tag[canonical].append(course)

        for skill, courses in by_tag.items():
            courses.sort(key=lambda item: (LEVEL_RANK.get(item.level, 99), item.title.lower()))
            grouped[skill] = courses[:max_per_skill]
        return grouped


class LiveApiRecommender(CourseRecommender):
    """Placeholder for a Coursera (or similar) catalog API."""

    name = "api"

    async def recommend(
        self,
        session: AsyncSession,
        missing_skills: list[str],
        *,
        max_per_skill: int = 3,
    ) -> dict[str, list[Course]]:
        raise NotImplementedError(
            "Live course API recommendations are not implemented yet. "
            "Set COURSE_RECOMMENDER=static to use the seeded courses table."
        )


class LLMCourseRecommender(CourseRecommender):
    """Placeholder for LLM-generated course suggestions."""

    name = "llm"

    async def recommend(
        self,
        session: AsyncSession,
        missing_skills: list[str],
        *,
        max_per_skill: int = 3,
    ) -> dict[str, list[Course]]:
        raise NotImplementedError(
            "LLM course recommendations are not implemented yet. "
            "Set COURSE_RECOMMENDER=static to use the seeded courses table."
        )


def get_recommender() -> CourseRecommender:
    method = settings.course_recommender.lower().strip()
    if method in {"static", "table", "db"}:
        return StaticTableRecommender()
    if method in {"api", "coursera", "live"}:
        return LiveApiRecommender()
    if method == "llm":
        return LLMCourseRecommender()
    raise ValueError(f"Unknown course recommender: {settings.course_recommender}")
