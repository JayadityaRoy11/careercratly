from fastapi import APIRouter, Query
from uuid import UUID

from app.core.exceptions import AppError
from app.core.openapi import ERROR_RESPONSES
from app.schemas.courses import CourseRecommendResponse
from app.services.ats_analyzer import UnknownRoleError, analyze_resume_against_role
from app.services.course_recommender import recommend_courses
from app.services.resume_store import resume_store

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get(
    "/recommend",
    response_model=CourseRecommendResponse,
    summary="Recommend courses for missing skills",
    description="Pass `skills` directly, or `resume_id` + `target_role` to use analysis gaps. Up to 3 courses per skill.",
    responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]},
)
async def recommend_courses_endpoint(
    skills: list[str] | None = Query(default=None),
    resume_id: UUID | None = Query(default=None),
    target_role: str | None = Query(default=None),
) -> CourseRecommendResponse:
    missing = list(skills or [])
    if not missing:
        if resume_id is None or not target_role:
            raise AppError(
                "Provide skills, or resume_id together with target_role.",
                code="bad_request",
                status_code=400,
            )
        stored = resume_store.get(resume_id)
        if stored is None:
            raise AppError("Resume not found. Upload a resume first.", code="not_found", status_code=404)
        try:
            analysis = analyze_resume_against_role(text=stored.text, target_role=target_role)
        except UnknownRoleError as exc:
            raise AppError(
                str(exc),
                code="unknown_role",
                status_code=422,
                details={"available_roles": exc.available},
            ) from None
        missing = analysis["missing_skills"]
    return CourseRecommendResponse.model_validate(recommend_courses(missing))
