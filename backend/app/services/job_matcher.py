from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.urls import is_safe_http_url
from app.providers.jobs import JobFilters, get_job_aggregator
from app.services.skill_extractor import get_skill_extractor


def search_jobs(filters: JobFilters | None = None) -> list[dict[str, Any]]:
    jobs = get_job_aggregator().search(filters or JobFilters())
    return [_public_job(job) for job in jobs][: settings.max_jobs]


def provider_statuses() -> list[dict[str, Any]]:
    return [
        {
            "provider": item.provider,
            "status": item.status,
            "message": item.message,
            "live": item.live,
        }
        for item in get_job_aggregator().statuses()
    ]


def match_jobs_to_resume(*, text: str, filters: JobFilters | None = None) -> list[dict[str, Any]]:
    extracted = set(get_skill_extractor().extract(text))
    ranked: list[dict[str, Any]] = []
    for job in get_job_aggregator().search(filters or JobFilters()):
        job_skills = list(job.get("skills") or [])
        matched = sorted(skill for skill in job_skills if skill in extracted)
        missing = [skill for skill in job_skills if skill not in extracted]
        coverage = (len(matched) / len(job_skills)) if job_skills else 0.0
        extra = len(extracted & set(job_skills))
        score = round(100 * (0.85 * coverage + 0.15 * min(1.0, extra / max(len(job_skills), 1))))
        ranked.append(
            {
                **_public_job(job),
                "match_score": score,
                "matched_skills": matched,
                "missing_skills": missing,
            }
        )
    ranked.sort(key=lambda item: (-item["match_score"], item["title"]))
    return ranked[: settings.max_jobs]


def _public_job(job: dict[str, Any]) -> dict[str, Any]:
    url = str(job.get("external_url") or "")
    if not is_safe_http_url(url):
        url = ""
    return {
        "id": job["id"],
        "title": job["title"],
        "company": job["company"],
        "location": job["location"],
        "work_mode": job["work_mode"],
        "employment_type": job["employment_type"],
        "skills": list(job.get("skills") or []),
        "description": job["description"],
        "source": job["source"],
        "source_logo": job.get("source_logo") or job.get("source"),
        "external_url": url,
        "posted_date": job["posted_date"],
        "is_demo": str(job.get("source")) == "mock",
    }
