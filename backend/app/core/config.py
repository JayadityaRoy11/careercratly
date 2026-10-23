from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "CareerCratly.AI"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    )

    upload_dir: str = "uploads"
    storage_backend: str = "local"
    max_resume_size_bytes: int = 5 * 1024 * 1024
    max_courses_per_skill: int = 3
    max_jobs: int = 50
    preload_extractor: bool = True
    job_provider: str = "mock"
    course_provider: str = "mock"
    project_provider: str = "static"

    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    linkedin_access_token: str = ""
    linkedin_api_version: str = "202603"
    linkedin_job_search_enabled: bool = False

    naukri_api_key: str = ""
    naukri_api_url: str = ""

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in {"dev", "development", "local", "test"}

    @property
    def cors_allow_origins(self) -> list[str]:
        if self.is_development:
            return ["*"]
        return self.cors_origins


settings = Settings()
