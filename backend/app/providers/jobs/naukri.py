from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.core.urls import is_safe_http_url
from app.providers.jobs.base import JobFilters, ProviderStatus


class NaukriJobProvider:
    """Official Naukri feed/API only. Never scrapes naukri.com."""

    name = "naukri"

    def status(self) -> ProviderStatus:
        if not (settings.naukri_api_key or "").strip() or not (settings.naukri_api_url or "").strip():
            return ProviderStatus(
                provider=self.name,
                status="not_configured",
                message="Naukri integration is not configured for this environment. "
                "An approved API/feed URL and key are required.",
                live=False,
            )
        if not is_safe_http_url(settings.naukri_api_url):
            return ProviderStatus(
                provider=self.name,
                status="not_configured",
                message="Naukri API URL is missing or not http(s).",
                live=False,
            )
        return ProviderStatus(
            provider=self.name,
            status="connected",
            message="Naukri feed credentials are configured.",
            live=True,
        )

    def search(self, filters: JobFilters) -> list[dict[str, Any]]:
        info = self.status()
        if info.status != "connected":
            return []
        try:
            response = httpx.get(
                settings.naukri_api_url,
                headers={"Authorization": f"Bearer {settings.naukri_api_key}"},
                params={
                    "role": filters.role or "",
                    "location": filters.location or "",
                    "work_mode": filters.work_mode or "",
                    "employment_type": filters.employment_type or "",
                },
                timeout=8.0,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return []
        rows = payload if isinstance(payload, list) else payload.get("items") or payload.get("jobs") or []
        jobs = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            url = str(row.get("external_url") or row.get("url") or "")
            if not is_safe_http_url(url):
                continue
            jobs.append(
                {
                    "id": str(row.get("id") or url),
                    "title": row.get("title") or "Untitled",
                    "company": row.get("company") or "Unknown",
                    "location": row.get("location") or "",
                    "work_mode": row.get("work_mode") or "onsite",
                    "employment_type": row.get("employment_type") or "full_time",
                    "skills": list(row.get("skills") or []),
                    "description": row.get("description") or "",
                    "source": "naukri",
                    "external_url": url,
                    "posted_date": str(row.get("posted_date") or ""),
                    "source_logo": "naukri",
                }
            )
        return jobs
