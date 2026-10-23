from __future__ import annotations

from typing import Any

from app.core.urls import is_safe_http_url
from app.data.loader import load_courses
from app.providers.courses.base import CourseProvider

FALLBACK_CATALOGS = [
    {
        "id": "fallback-coursera",
        "title": "Coursera catalog",
        "provider": "Coursera",
        "url": "https://www.coursera.org/",
        "level": "beginner",
        "placeholder": True,
    },
    {
        "id": "fallback-edx",
        "title": "edX catalog",
        "provider": "edX",
        "url": "https://www.edx.org/",
        "level": "beginner",
        "placeholder": True,
    },
    {
        "id": "fallback-microsoft",
        "title": "Microsoft Learn",
        "provider": "Microsoft Learn",
        "url": "https://learn.microsoft.com/",
        "level": "beginner",
        "placeholder": True,
    },
]


class MockCourseProvider:
    name = "mock"

    def recommend(self, skill: str, *, limit: int) -> list[dict[str, Any]]:
        key = skill.strip().lower()
        matches = [
            course
            for course in load_courses()
            if str(course.get("skill_tag") or "").lower() == key and is_safe_http_url(course["url"])
        ]
        if not matches:
            matches = [
                course
                for course in FALLBACK_CATALOGS
                if is_safe_http_url(course["url"])
            ]
        out = []
        for course in matches[:limit]:
            out.append(
                {
                    "id": course["id"],
                    "title": course["title"],
                    "provider": course["provider"],
                    "skill_tag": course.get("skill_tag", skill),
                    "level": course.get("level"),
                    "url": course["url"],
                    "placeholder": bool(course.get("placeholder")),
                }
            )
        return out


def get_course_provider() -> CourseProvider:
    return MockCourseProvider()
