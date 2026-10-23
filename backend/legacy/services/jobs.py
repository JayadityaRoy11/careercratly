from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.loader import skill_alias_map
from app.db.seed import get_job_role_by_type
from app.models.job import Application, ApplicationStatus, Job
from app.models.resume import Resume
from app.models.user import User
from app.services.analysis import match_resume_to_required_skills


def canonicalize_skills(skills: list[str]) -> list[str]:
    aliases = skill_alias_map()
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in skills:
        name = raw.strip()
        if not name:
            continue
        canonical = aliases.get(name.lower(), name)
        key = canonical.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(canonical)
    return ordered


async def create_job(
    session: AsyncSession,
    *,
    recruiter: User,
    title: str,
    description: str,
    required_skills: list[str],
    location: str,
    job_type: str,
) -> Job:
    skills = canonicalize_skills(required_skills)
    if not skills:
        raise ValueError("At least one required skill is needed")

    job = Job(
        recruiter_id=recruiter.id,
        title=title.strip(),
        description=description.strip(),
        required_skills=skills,
        location=location.strip(),
        job_type=job_type.strip(),
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


def _jobs_query(
    *,
    job_type: str | None,
    skill: str | None,
    location: str | None,
    q: str | None,
) -> Select[tuple[Job]]:
    stmt = select(Job).order_by(Job.created_at.desc())
    if job_type:
        key = job_type.strip()
        slug = key.lower().replace(" ", "_").replace("-", "_")
        stmt = stmt.where(
            or_(
                Job.job_type.ilike(key),
                func.lower(func.replace(Job.job_type, " ", "_")) == slug,
            )
        )
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location.strip()}%"))
    if q:
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(Job.title.ilike(term), Job.description.ilike(term)))
    if skill:
        canonical = canonicalize_skills([skill])
        needle = canonical[0] if canonical else skill.strip()
        stmt = stmt.where(Job.required_skills.contains([needle]))
    return stmt


async def list_jobs(
    session: AsyncSession,
    *,
    job_type: str | None = None,
    skill: str | None = None,
    location: str | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Job], int]:
    base = _jobs_query(job_type=job_type, skill=skill, location=location, q=q)
    total = await session.scalar(select(func.count()).select_from(base.subquery())) or 0
    stmt = base.limit(min(limit, 100)).offset(max(offset, 0))
    result = await session.execute(stmt)
    return list(result.scalars().all()), int(total)


async def get_job(session: AsyncSession, job_id: UUID) -> Job | None:
    result = await session.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def apply_to_job(
    session: AsyncSession,
    *,
    job: Job,
    candidate: User,
    resume: Resume,
) -> Application:
    weights: dict[str, float] | None = None
    role = await get_job_role_by_type(session, job.job_type)
    if role is not None:
        weights = {link.skill.name: link.weight for link in role.skill_links}

    match = await match_resume_to_required_skills(
        resume.raw_text,
        list(job.required_skills or []),
        weights=weights,
    )

    application = Application(
        job_id=job.id,
        candidate_id=candidate.id,
        resume_id=resume.id,
        status=ApplicationStatus.APPLIED,
        match_score=match.match_score,
    )
    job_id = job.id
    candidate_id = candidate.id
    session.add(application)
    try:
        await session.commit()
        await session.refresh(application)
    except IntegrityError:
        await session.rollback()
        raise DuplicateApplicationError(job_id, candidate_id) from None
    return application


async def list_applicants(
    session: AsyncSession,
    *,
    job: Job,
) -> list[Application]:
    result = await session.execute(
        select(Application)
        .options(selectinload(Application.candidate))
        .where(Application.job_id == job.id)
        .order_by(Application.match_score.desc(), Application.applied_at.asc())
    )
    return list(result.scalars().all())


class DuplicateApplicationError(Exception):
    def __init__(self, job_id: UUID, candidate_id: UUID) -> None:
        self.job_id = job_id
        self.candidate_id = candidate_id
        super().__init__("You have already applied to this job")
