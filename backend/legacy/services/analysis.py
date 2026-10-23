from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed import get_job_role_by_type, list_job_roles
from app.models.resume import Resume
from app.models.skill import ResumeAnalysis
from app.schemas.analysis import ResumeAnalysisPublic
from app.services.matching import MatchResult, WeightedSkill, score_skills
from app.services.skill_extractor import get_skill_extractor


class UnknownJobTypeError(Exception):
    def __init__(self, job_type: str, available: list[str]) -> None:
        self.job_type = job_type
        self.available = available
        super().__init__(f"Unknown job type: {job_type}")


async def match_resume_to_required_skills(
    raw_text: str,
    required_skills: list[str],
    *,
    weights: dict[str, float] | None = None,
) -> MatchResult:
    """Extract skills from resume text and score them against a required list."""
    weight_map = {key.lower(): value for key, value in (weights or {}).items()}
    required = [
        WeightedSkill(
            name=name.strip(),
            weight=weight_map.get(name.strip().lower(), 1.0),
        )
        for name in required_skills
        if isinstance(name, str) and name.strip()
    ]
    extractor = get_skill_extractor()
    extracted = await asyncio.to_thread(extractor.extract, raw_text)
    return score_skills(extracted, required)


async def analyze_resume(
    session: AsyncSession,
    *,
    resume: Resume,
    job_type: str,
) -> ResumeAnalysisPublic:
    role = await get_job_role_by_type(session, job_type)
    if role is None:
        roles = await list_job_roles(session)
        raise UnknownJobTypeError(job_type, [item.name for item in roles])

    required_names = [link.skill.name for link in role.skill_links]
    weights = {link.skill.name: link.weight for link in role.skill_links}
    result = await match_resume_to_required_skills(
        resume.raw_text,
        required_names,
        weights=weights,
    )
    extractor_name = get_skill_extractor().name

    matched_payload = [{"name": s.name, "weight": s.weight} for s in result.matched_skills]
    missing_payload = [{"name": s.name, "weight": s.weight} for s in result.missing_skills]

    analysis = await _get_existing(session, resume.id, role.slug)
    now = datetime.now(timezone.utc)
    if analysis is None:
        analysis = ResumeAnalysis(
            resume_id=resume.id,
            job_type=role.slug,
            matched_skills=matched_payload,
            missing_skills=missing_payload,
            match_score=result.match_score,
            extractor=extractor_name,
            analyzed_at=now,
        )
        session.add(analysis)
    else:
        analysis.matched_skills = matched_payload
        analysis.missing_skills = missing_payload
        analysis.match_score = result.match_score
        analysis.extractor = extractor_name
        analysis.analyzed_at = now

    await session.commit()
    await session.refresh(analysis)
    return ResumeAnalysisPublic(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_type=role.name,
        matched_skills=analysis.matched_skills,
        missing_skills=analysis.missing_skills,
        match_score=analysis.match_score,
        extractor=analysis.extractor,
        analyzed_at=analysis.analyzed_at,
    )


async def get_resume_analysis(
    session: AsyncSession,
    resume_id: UUID,
    job_type: str,
) -> ResumeAnalysis | None:
    result = await session.execute(
        select(ResumeAnalysis).where(
            ResumeAnalysis.resume_id == resume_id,
            ResumeAnalysis.job_type == job_type,
        )
    )
    return result.scalar_one_or_none()


async def _get_existing(
    session: AsyncSession,
    resume_id: UUID,
    job_type: str,
) -> ResumeAnalysis | None:
    return await get_resume_analysis(session, resume_id, job_type)
