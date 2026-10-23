from fastapi import APIRouter, Query

from app.core.exceptions import AppError
from app.core.openapi import ERROR_RESPONSES
from app.models.job import EmploymentType, WorkMode
from app.providers.jobs import JobFilters
from app.schemas.jobs import (
    JobListResponse,
    JobMatchRequest,
    JobMatchResponse,
    JobSearchResponse,
    JobSourcesResponse,
)
from app.services.job_matcher import match_jobs_to_resume, provider_statuses, search_jobs
from app.services.resume_store import resume_store

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _filters(
    *,
    role: str | None,
    location: str | None,
    work_mode: WorkMode | None,
    employment_type: EmploymentType | None,
    experience_level: str | None,
    source: str | None,
    skills: list[str] | None,
) -> JobFilters:
    return JobFilters(
        role=role,
        location=location,
        work_mode=work_mode.value if work_mode else None,
        employment_type=employment_type.value if employment_type else None,
        experience_level=experience_level,
        source=source,
        skills=skills or [],
    )


@router.get(
    "/sources",
    response_model=JobSourcesResponse,
    summary="Job provider status",
)
async def job_sources() -> JobSourcesResponse:
    return JobSourcesResponse(sources=provider_statuses())


@router.get(
    "",
    response_model=JobListResponse,
    summary="List jobs from connected providers plus demo fallback",
)
async def list_jobs() -> JobListResponse:
    items = search_jobs()
    return JobListResponse(items=items, count=len(items), sources=provider_statuses())


@router.get(
    "/search",
    response_model=JobSearchResponse,
    summary="Search jobs",
)
async def search_jobs_endpoint(
    role: str | None = Query(default=None, example="backend"),
    location: str | None = Query(default=None, example="Bengaluru"),
    work_mode: WorkMode | None = Query(default=None),
    employment_type: EmploymentType | None = Query(default=None),
    experience_level: str | None = Query(default=None),
    source: str | None = Query(default=None, description="all | mock | linkedin | naukri"),
    skills: list[str] | None = Query(default=None),
) -> JobSearchResponse:
    items = search_jobs(
        _filters(
            role=role,
            location=location,
            work_mode=work_mode,
            employment_type=employment_type,
            experience_level=experience_level,
            source=source,
            skills=skills,
        )
    )
    return JobSearchResponse(items=items, count=len(items), sources=provider_statuses())


@router.post(
    "/match",
    response_model=JobMatchResponse,
    summary="Rank jobs against an uploaded resume",
    responses={404: ERROR_RESPONSES[404]},
)
async def match_jobs(payload: JobMatchRequest) -> JobMatchResponse:
    stored = resume_store.get(payload.resume_id)
    if stored is None:
        raise AppError("Resume not found. Upload a resume first.", code="not_found", status_code=404)
    items = match_jobs_to_resume(
        text=stored.text,
        filters=_filters(
            role=payload.role,
            location=payload.location,
            work_mode=payload.work_mode,
            employment_type=payload.employment_type,
            experience_level=payload.experience_level,
            source=payload.source,
            skills=payload.skills,
        ),
    )
    return JobMatchResponse(
        resume_id=payload.resume_id,
        items=items,
        count=len(items),
        sources=provider_statuses(),
    )
