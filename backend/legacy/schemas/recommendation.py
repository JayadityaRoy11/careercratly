from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.course import CourseLevel
from app.schemas.analysis import WeightedSkillOut


class CoursePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    provider: str
    url: str
    skill_tag: str
    level: CourseLevel


class SkillCourseGroup(BaseModel):
    skill: str
    weight: float
    courses: list[CoursePublic]


class RecommendationsResponse(BaseModel):
    resume_id: UUID
    job_type: str
    missing_skills: list[WeightedSkillOut]
    recommendations: list[SkillCourseGroup]
    recommender: str = Field(description="Backend used: static, api, or llm")
