from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"job_type": "AI Engineer"}]}
    )

    job_type: str = Field(
        min_length=1,
        examples=["AI Engineer", "data_analyst", "Backend Developer"],
    )


class WeightedSkillOut(BaseModel):
    name: str
    weight: float


class ResumeAnalysisPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resume_id: UUID
    job_type: str
    matched_skills: list[WeightedSkillOut]
    missing_skills: list[WeightedSkillOut]
    match_score: float
    extractor: str
    analyzed_at: datetime
