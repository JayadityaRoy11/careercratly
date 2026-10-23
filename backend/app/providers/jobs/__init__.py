from app.providers.jobs.aggregator import JobAggregator, get_job_aggregator
from app.providers.jobs.base import JobFilters, JobProvider, ProviderStatus
from app.providers.jobs.linkedin import LinkedInJobProvider
from app.providers.jobs.mock import MockJobProvider
from app.providers.jobs.naukri import NaukriJobProvider


def get_job_provider() -> JobProvider:
    return get_job_aggregator()


__all__ = [
    "JobAggregator",
    "JobFilters",
    "JobProvider",
    "LinkedInJobProvider",
    "MockJobProvider",
    "NaukriJobProvider",
    "ProviderStatus",
    "get_job_aggregator",
    "get_job_provider",
]
