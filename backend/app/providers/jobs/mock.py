from __future__ import annotations

from typing import Any

from app.core.urls import is_safe_http_url
from app.data.loader import load_jobs
from app.providers.jobs.base import JobFilters, JobProvider


class MockJobProvider:
    """Static demo listings. Not scraped from LinkedIn, Naukri, or Indeed."""

    name = "mock"

    def status(self):
        from app.providers.jobs.base import ProviderStatus

        return ProviderStatus(
            provider=self.name,
            status="demo",
            message="Demo listings are available. They are not live vacancies.",
            live=False,
        )

    def search(self, filters: JobFilters) -> list[dict[str, Any]]:
        jobs = [job for job in load_jobs() if is_safe_http_url(str(job.get("external_url") or ""))]
        if filters.role:
            needle = filters.role.lower()
            jobs = [
                job
                for job in jobs
                if needle in job["title"].lower()
                or needle in " ".join(job.get("skills") or []).lower()
                or needle in job["description"].lower()
            ]
        if filters.location:
            needle = filters.location.lower()
            if needle in {"bangalore", "bengaluru"}:
                jobs = [
                    job
                    for job in jobs
                    if "bengaluru" in job["location"].lower() or "bangalore" in job["location"].lower()
                ]
            else:
                jobs = [job for job in jobs if needle in job["location"].lower()]
        if filters.work_mode:
            jobs = [job for job in jobs if job["work_mode"] == filters.work_mode]
        if filters.employment_type:
            jobs = [job for job in jobs if job["employment_type"] == filters.employment_type]
        if filters.skills:
            wanted = {skill.lower() for skill in filters.skills}
            jobs = [
                job
                for job in jobs
                if wanted <= {skill.lower() for skill in job.get("skills") or []}
            ]
        if filters.experience_level:
            level = filters.experience_level.lower()
            jobs = [
                job
                for job in jobs
                if level in (job.get("experience_level") or "").lower()
                or (level == "internship" and job.get("employment_type") == "internship")
                or (level == "entry" and "intern" not in job["title"].lower())
                or (level == "mid" and any(token in job["title"].lower() for token in ("senior", "ii", "mid")))
            ]
        return [{**job, "is_demo": True} for job in jobs]


def get_job_provider() -> JobProvider:
    return MockJobProvider()
