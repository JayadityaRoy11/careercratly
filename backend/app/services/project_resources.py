from __future__ import annotations

from typing import Any

from app.providers.research import get_project_resource_provider


def get_project_resources(topic: str) -> dict[str, Any]:
    return get_project_resource_provider().resources_for(topic)
