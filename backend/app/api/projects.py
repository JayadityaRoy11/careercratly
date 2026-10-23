from fastapi import APIRouter, Query

from app.schemas.courses import ProjectResourcesResponse
from app.services.project_resources import get_project_resources

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "/resources",
    response_model=ProjectResourcesResponse,
    summary="Project and research links",
    description="Landing and search URLs only. Does not return copyrighted paper text.",
)
async def project_resources(
    topic: str = Query(..., example="RAG chatbot over a document corpus"),
) -> ProjectResourcesResponse:
    return ProjectResourcesResponse.model_validate(get_project_resources(topic))
