from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.providers.jobs.base import JobFilters, ProviderStatus


class LinkedInJobProvider:
    """Authorized LinkedIn Talent access only.

    LinkedIn's documented Jobs APIs are partner Job *Posting* APIs (Talent Solutions),
    not a public job-search feed. This adapter never scrapes linkedin.com.
    """

    name = "linkedin"

    def status(self) -> ProviderStatus:
        token = (settings.linkedin_access_token or "").strip()
        search_enabled = settings.linkedin_job_search_enabled
        if not token or not search_enabled:
            return ProviderStatus(
                provider=self.name,
                status="not_configured",
                message="LinkedIn integration is not configured for this environment. "
                "Job search requires authorized Talent Solutions partner access; "
                "there is no public LinkedIn job-search API.",
                live=False,
            )
        return ProviderStatus(
            provider=self.name,
            status="not_configured",
            message="LinkedIn credentials are present, but this product does not call a job-search endpoint. "
            "LinkedIn Job Posting APIs post jobs; they do not provide a general job search.",
            live=False,
        )

    def search(self, filters: JobFilters) -> list[dict[str, Any]]:
        return []
