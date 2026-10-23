from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from app.core.urls import is_safe_http_url
from app.data.loader import load_projects
from app.providers.research.base import ProjectResourceProvider


class StaticProjectResourceProvider:
    name = "static"

    def resources_for(self, topic: str) -> dict[str, Any]:
        catalog = load_projects()
        key = topic.strip()
        resources = catalog.get(key)
        if resources is None:
            lowered = key.lower()
            for name, items in catalog.items():
                if name.lower() == lowered:
                    resources = items
                    key = name
                    break
        if resources is None:
            q = quote_plus(key)
            resources = [
                {
                    "title": f"Google Scholar: {key}",
                    "type": "research",
                    "source": "Google Scholar",
                    "url": f"https://scholar.google.com/scholar?q={q}",
                },
                {
                    "title": f"arXiv search: {key}",
                    "type": "research",
                    "source": "arXiv",
                    "url": f"https://arxiv.org/search/?query={q}&searchtype=all",
                },
                {
                    "title": f"Papers with Code search: {key}",
                    "type": "research",
                    "source": "Papers with Code",
                    "url": f"https://paperswithcode.com/search?q={q}",
                },
                {
                    "title": f"Kaggle search: {key}",
                    "type": "dataset",
                    "source": "Kaggle",
                    "url": f"https://www.kaggle.com/search?q={q}",
                },
                {
                    "title": f"GitHub topics/search: {key}",
                    "type": "github",
                    "source": "GitHub",
                    "url": f"https://github.com/search?q={q}&type=repositories",
                },
            ]
        safe = [item for item in resources if is_safe_http_url(str(item.get("url") or ""))]
        return {"topic": key, "resources": safe}


def get_project_resource_provider() -> ProjectResourceProvider:
    return StaticProjectResourceProvider()
