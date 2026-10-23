from __future__ import annotations

from typing import Any, Protocol


class CourseProvider(Protocol):
    name: str

    def recommend(self, skill: str, *, limit: int) -> list[dict[str, Any]]:
        """Return catalog rows for a skill. Replace with a licensed catalog API later."""
