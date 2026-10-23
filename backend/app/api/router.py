from fastapi import APIRouter

from app.api import courses, health, interview, jobs, projects, resume

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(resume.router)
api_router.include_router(jobs.router)
api_router.include_router(courses.router)
api_router.include_router(projects.router)
api_router.include_router(interview.router)
