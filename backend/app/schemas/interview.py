from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    id: str
    question: str


class InterviewQuestionsResponse(BaseModel):
    role: str
    difficulty: str
    questions: list[InterviewQuestion]


class InterviewEvaluateRequest(BaseModel):
    role: str = Field(examples=["Backend Developer"])
    question: str
    answer: str


class InterviewEvaluateResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    keyword_coverage: int
    technical_relevance: int
    structure_score: int
    strengths: list[str]
    missing_keywords: list[str]
    suggestions: list[str]
