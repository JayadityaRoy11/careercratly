from fastapi import APIRouter, Query

from app.schemas.interview import (
    InterviewEvaluateRequest,
    InterviewEvaluateResponse,
    InterviewQuestionsResponse,
)
from app.services.interview_analyzer import evaluate_answer, list_questions

router = APIRouter(prefix="/interview", tags=["interview"])


@router.get(
    "/questions",
    response_model=InterviewQuestionsResponse,
    summary="Interview questions",
    description="Prototype question bank by role and difficulty. Text only — no video or emotion analysis.",
)
async def interview_questions(
    role: str = Query(..., example="Backend Developer"),
    difficulty: str = Query(default="medium", example="medium"),
) -> InterviewQuestionsResponse:
    return InterviewQuestionsResponse.model_validate(list_questions(role=role, difficulty=difficulty))


@router.post(
    "/evaluate",
    response_model=InterviewEvaluateResponse,
    summary="Evaluate a text interview answer",
    description="Deterministic keyword and structure scoring. Suitable for later speech-to-text input.",
)
async def interview_evaluate(payload: InterviewEvaluateRequest) -> InterviewEvaluateResponse:
    return InterviewEvaluateResponse.model_validate(
        evaluate_answer(role=payload.role, question=payload.question, answer=payload.answer)
    )
