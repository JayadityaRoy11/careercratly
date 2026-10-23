from uuid import UUID

from pydantic import BaseModel, Field

from app.models.job import EmploymentType, WorkMode


class JobPublic(BaseModel):
    id: str
    title: str
    company: str
    location: str
    work_mode: WorkMode
    employment_type: EmploymentType
    skills: list[str]
    description: str
    source: str
    source_logo: str | None = None
    external_url: str = Field(examples=["https://www.python.org/jobs/"])
    posted_date: str
    is_demo: bool = True


class MatchedJob(JobPublic):
    match_score: int = Field(ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]


class ProviderStatusPublic(BaseModel):
    provider: str
    status: str
    message: str
    live: bool = False


class JobListResponse(BaseModel):
    items: list[JobPublic]
    count: int
    sources: list[ProviderStatusPublic] = Field(default_factory=list)


class JobSearchResponse(JobListResponse):
    pass


class JobMatchRequest(BaseModel):
    resume_id: UUID
    role: str | None = None
    location: str | None = None
    work_mode: WorkMode | None = None
    employment_type: EmploymentType | None = None
    experience_level: str | None = None
    source: str | None = None
    skills: list[str] = Field(default_factory=list)


class JobMatchResponse(BaseModel):
    resume_id: UUID
    items: list[MatchedJob]
    count: int
    sources: list[ProviderStatusPublic] = Field(default_factory=list)


class JobSourcesResponse(BaseModel):
    sources: list[ProviderStatusPublic]
