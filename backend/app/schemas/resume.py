from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ResumeParseResult(BaseModel):
    filename: str = Field(examples=["jane-doe-resume.pdf"])
    file_type: str = Field(examples=["pdf"])
    text: str
    pages: int = Field(examples=[1])
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResumeUploadResponse(ResumeParseResult):
    resume_id: UUID
    extracted_skills: list[str] = Field(default_factory=list)


class ResumeAnalyzeRequest(BaseModel):
    resume_id: UUID
    target_role: str = Field(
        examples=["Backend Developer"],
        description="Role name or slug, e.g. Backend Developer or backend_developer.",
    )


class PartialMatch(BaseModel):
    skill: str
    related_found: str
    note: str


class ScoreComponents(BaseModel):
    required_skill_coverage: float
    preferred_skill_coverage: float
    keyword_relevance: float
    experience_project_relevance: float
    resume_section_completeness: float


class ResumeAnalyzeResponse(BaseModel):
    resume_id: UUID
    score: int = Field(ge=0, le=100, examples=[82])
    score_label: str = "Resume Match Score"
    target_role: str
    target_role_slug: str
    matched_skills: list[str]
    missing_skills: list[str]
    partial_matches: list[PartialMatch]
    strengths: list[str]
    improvements: list[str]
    recommended_keywords: list[str]
    recommended_certifications: list[str] = Field(default_factory=list)
    recommended_project_themes: list[str] = Field(default_factory=list)
    components: ScoreComponents
    disclaimer: str
    extracted_skills: list[str]
    intelligence: dict[str, Any] = Field(default_factory=dict)
