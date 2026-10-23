from fastapi import APIRouter, File, UploadFile, status

from app.core.exceptions import AppError
from app.core.openapi import ERROR_RESPONSES
from app.schemas.resume import ResumeAnalyzeRequest, ResumeAnalyzeResponse, ResumeUploadResponse
from app.services.ats_analyzer import UnknownRoleError, analyze_resume_against_role
from app.services.resume_store import resume_store
from app.services.resume_upload import upload_and_parse

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a resume",
    description="Accept a PDF or DOCX (max 5MB). Extract text in-memory for the prototype session.",
    responses={413: ERROR_RESPONSES[413], 415: ERROR_RESPONSES[415], 422: ERROR_RESPONSES[422]},
)
async def upload_resume(
    file: UploadFile = File(..., description="PDF or DOCX resume, max 5MB"),
) -> ResumeUploadResponse:
    payload = await upload_and_parse(file)
    return ResumeUploadResponse.model_validate(payload)


@router.post(
    "/analyze",
    response_model=ResumeAnalyzeResponse,
    summary="Analyze resume vs a target role",
    description="Compute an explainable Resume Match Score. Deterministic for the same text and role.",
    responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]},
)
async def analyze_resume(payload: ResumeAnalyzeRequest) -> ResumeAnalyzeResponse:
    stored = resume_store.get(payload.resume_id)
    if stored is None:
        raise AppError("Resume not found. Upload a resume first.", code="not_found", status_code=404)
    try:
        analysis = analyze_resume_against_role(text=stored.text, target_role=payload.target_role)
    except UnknownRoleError as exc:
        raise AppError(
            str(exc),
            code="unknown_role",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"available_roles": exc.available},
        ) from None
    return ResumeAnalyzeResponse(resume_id=stored.id, **analysis)
