from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import ApplicationStatus
from app.schemas.auth import UserPublic


class JobCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Senior Backend Engineer",
                    "description": "Build APIs with FastAPI and PostgreSQL.",
                    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                    "location": "Remote",
                    "job_type": "Backend Developer",
                }
            ]
        }
    )

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    required_skills: list[str] = Field(min_length=1)
    location: str = Field(min_length=1, max_length=255)
    job_type: str = Field(min_length=1, max_length=120)


class JobPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recruiter_id: UUID
    title: str
    description: str
    required_skills: list[str]
    location: str
    job_type: str
    created_at: datetime


class JobApplyRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"resume_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}]
        }
    )

    resume_id: UUID


class ApplicationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    candidate_id: UUID
    resume_id: UUID
    status: ApplicationStatus
    match_score: float
    applied_at: datetime


class ApplicantPublic(ApplicationPublic):
    candidate: UserPublic
