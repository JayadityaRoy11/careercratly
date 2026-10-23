from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.seed import get_job_role_by_type, list_job_roles
from app.models.resume import Resume
from app.schemas.recommendation import (
    CoursePublic,
    RecommendationsResponse,
    SkillCourseGroup,
)
from app.services.analysis import UnknownJobTypeError, get_resume_analysis
from app.services.recommender import get_recommender


async def recommend_courses_for_resume(
    session: AsyncSession,
    *,
    resume: Resume,
    job_type: str,
) -> RecommendationsResponse:
    role = await get_job_role_by_type(session, job_type)
    if role is None:
        roles = await list_job_roles(session)
        raise UnknownJobTypeError(job_type, [item.name for item in roles])

    analysis = await get_resume_analysis(session, resume.id, role.slug)
    if analysis is None:
        raise AnalysisNotFoundError(resume.id, role.name)

    missing = list(analysis.missing_skills or [])
    skill_names = [item["name"] for item in missing if item.get("name")]
    weights = {item["name"]: float(item.get("weight", 0)) for item in missing}

    recommender = get_recommender()
    grouped = await recommender.recommend(
        session,
        skill_names,
        max_per_skill=settings.max_courses_per_skill,
    )

    recommendations = [
        SkillCourseGroup(
            skill=name,
            weight=weights.get(name, 0),
            courses=[CoursePublic.model_validate(course) for course in grouped.get(name, [])],
        )
        for name in skill_names
    ]
    return RecommendationsResponse(
        resume_id=resume.id,
        job_type=role.name,
        missing_skills=missing,
        recommendations=recommendations,
        recommender=recommender.name,
    )


class AnalysisNotFoundError(Exception):
    def __init__(self, resume_id: UUID, job_type: str) -> None:
        self.resume_id = resume_id
        self.job_type = job_type
        super().__init__(
            f"No analysis found for this resume and job type '{job_type}'. "
            "POST /resume/{id}/analyze first."
        )
