from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent


def _read_json(filename: str) -> Any:
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_skills() -> list[dict[str, Any]]:
    return _read_json("skills.json")


@lru_cache(maxsize=1)
def load_roles() -> list[dict[str, Any]]:
    return _read_json("roles.json")


@lru_cache(maxsize=1)
def load_jobs() -> list[dict[str, Any]]:
    return _read_json("jobs.json")


@lru_cache(maxsize=1)
def load_courses() -> list[dict[str, Any]]:
    return _read_json("courses.json")


@lru_cache(maxsize=1)
def load_projects() -> dict[str, Any]:
    return _read_json("projects.json")


@lru_cache(maxsize=1)
def load_interview() -> dict[str, Any]:
    return _read_json("interview.json")


def skill_alias_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for skill in load_skills():
        canonical = skill["name"]
        mapping[canonical.lower()] = canonical
        for alias in skill.get("aliases") or []:
            mapping[str(alias).lower()] = canonical
    return mapping


def get_role(name_or_slug: str) -> dict[str, Any] | None:
    key = name_or_slug.strip().lower().replace("-", " ").replace("_", " ")
    slug = name_or_slug.strip().lower().replace(" ", "_").replace("-", "_")
    for role in load_roles():
        if role["slug"] == slug:
            return role
        if role["name"].lower() == name_or_slug.strip().lower():
            return role
        if role["name"].lower().replace("-", " ") == key:
            return role
    return None
