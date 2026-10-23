OPENAPI_TAGS = [
    {"name": "health", "description": "Service liveness."},
    {"name": "resume", "description": "Upload a resume and run an explainable match analysis."},
    {"name": "jobs", "description": "Search demo jobs and rank them against a resume. Mock data only."},
    {"name": "courses", "description": "Course and certification suggestions for missing skills."},
    {"name": "projects", "description": "Public project, dataset, and research links for a topic."},
    {"name": "interview", "description": "Prototype interview questions and text-answer evaluation."},
]

APP_DESCRIPTION = """
CareerCratly.AI — academic prototype of an AI-powered career platform.

Upload a PDF/DOCX resume, analyze it against a target role, get an explainable
Resume Match Score, course ideas, project resources, ranked demo jobs with
external apply URLs, and a lightweight interview-prep API.

This build has **no authentication**. Job listings are mock/demo data served
through a `JobProvider` interface — not scraped from LinkedIn, Naukri, or Indeed.
"""

ERROR_RESPONSES = {
    400: {"description": "Bad request"},
    404: {"description": "Not found"},
    413: {"description": "File too large"},
    415: {"description": "Unsupported media type"},
    422: {"description": "Unprocessable entity"},
}
