from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class WorkMode(str, Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"


class EmploymentType(str, Enum):
    internship = "internship"
    full_time = "full_time"
    part_time = "part_time"


class StoredResumeModel(BaseModel):
    id: UUID
    filename: str
    file_type: str
    text: str
    pages: int
    metadata: dict[str, Any]
    created_at: datetime


class JobListing(BaseModel):
    id: str
    title: str
    company: str
    location: str
    work_mode: WorkMode
    employment_type: EmploymentType
    skills: list[str]
    description: str
    source: str
    external_url: HttpUrl | str
    posted_date: str


class CourseListing(BaseModel):
    id: str
    title: str
    provider: str
    skill_tag: str
    level: str | None = None
    url: str
    placeholder: bool = False
