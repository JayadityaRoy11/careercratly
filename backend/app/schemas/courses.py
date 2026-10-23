from pydantic import BaseModel, Field


class CoursePublic(BaseModel):
    id: str
    title: str
    provider: str
    skill_tag: str
    level: str | None = None
    url: str
    placeholder: bool = False


class SkillCourseGroup(BaseModel):
    skill: str
    courses: list[CoursePublic]


class CourseRecommendResponse(BaseModel):
    recommendations: list[SkillCourseGroup]


class ProjectResource(BaseModel):
    title: str
    type: str = Field(description="research | dataset | github | tutorial")
    source: str
    url: str


class ProjectResourcesResponse(BaseModel):
    topic: str
    resources: list[ProjectResource]
