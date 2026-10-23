from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.providers.jobs.base import JobFilters, ProviderStatus
from app.providers.jobs.linkedin import LinkedInJobProvider
from app.providers.jobs.mock import MockJobProvider
from app.providers.jobs.naukri import NaukriJobProvider


class JobAggregator:
    def __init__(self) -> None:
        self.providers = {
            "linkedin": LinkedInJobProvider(),
            "naukri": NaukriJobProvider(),
            "mock": MockJobProvider(),
        }

    def statuses(self) -> list[ProviderStatus]:
        return [provider.status() for provider in self.providers.values()]

    def search(self, filters: JobFilters) -> list[dict[str, Any]]:
        requested = (filters.source or "all").lower()
        names = list(self.providers) if requested in {"", "all"} else [requested]
        jobs: list[dict[str, Any]] = []
        seen: set[str] = set()
        for name in names:
            provider = self.providers.get(name)
            if provider is None:
                continue
            if name != "mock" and provider.status().status != "connected":
                continue
            for job in provider.search(filters):
                job_id = str(job.get("id"))
                if job_id in seen:
                    continue
                seen.add(job_id)
                job.setdefault("source_logo", job.get("source"))
                jobs.append(job)
        if requested in {"", "all"}:
            for job in self.providers["mock"].search(filters):
                job_id = str(job.get("id"))
                if job_id in seen:
                    continue
                seen.add(job_id)
                job.setdefault("source_logo", "mock")
                jobs.append(job)
        elif requested == "mock" and not jobs:
            jobs = self.providers["mock"].search(filters)
        return jobs[: settings.max_jobs]


_aggregator: JobAggregator | None = None


def get_job_aggregator() -> JobAggregator:
    global _aggregator
    if _aggregator is None:
        _aggregator = JobAggregator()
    return _aggregator
