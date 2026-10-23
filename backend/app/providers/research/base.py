from __future__ import annotations

from typing import Any, Protocol


class ProjectResourceProvider(Protocol):
    name: str

    def resources_for(self, topic: str) -> dict[str, Any]:
        """Public search/landing links only — not copyrighted paper text."""
