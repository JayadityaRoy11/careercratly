from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

ProviderStatusCode = Literal["connected", "demo", "not_configured", "error"]


@dataclass
class JobFilters:
    role: str | None = None
    location: str | None = None
    work_mode: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    skills: list[str] = field(default_factory=list)
    source: str | None = None


@dataclass
class ProviderStatus:
    provider: str
    status: ProviderStatusCode
    message: str
    live: bool = False


class JobProvider(Protocol):
    name: str

    def status(self) -> ProviderStatus: ...

    def search(self, filters: JobFilters) -> list[dict[str, Any]]:
        """Return normalized job dicts. Never scrape third-party career sites."""
