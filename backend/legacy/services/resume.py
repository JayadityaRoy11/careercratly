from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.services.resume_parser import ResumeParseError, detect_extension, extract_text
from app.services.storage import StorageService, get_storage_service


class ResumeTooLargeError(Exception):
    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes
        super().__init__(f"File exceeds the {max_bytes} byte limit")


def sanitize_filename(filename: str | None) -> str:
    name = Path(filename or "resume").name.strip() or "resume"
    return name[:255]


async def read_upload_limited(file_reader, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file_reader(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ResumeTooLargeError(max_bytes)
        chunks.append(chunk)
    return b"".join(chunks)


async def create_parsed_resume(
    session: AsyncSession,
    *,
    user_id: UUID,
    filename: str,
    file_bytes: bytes,
    storage: StorageService | None = None,
) -> Resume:
    safe_name = sanitize_filename(filename)
    resume_id = uuid4()
    extension = detect_extension(safe_name)
    storage_key = f"{user_id}/{resume_id}{extension}"
    storage = storage or get_storage_service()

    raw_text = extract_text(file_bytes, safe_name)
    await storage.save(file_bytes, storage_key)

    resume = Resume(
        id=resume_id,
        user_id=user_id,
        filename=safe_name,
        raw_text=raw_text,
    )
    session.add(resume)
    try:
        await session.commit()
        await session.refresh(resume)
    except Exception:
        await storage.delete(storage_key)
        await session.rollback()
        raise
    return resume


async def get_resume_for_user(
    session: AsyncSession,
    *,
    resume_id: UUID,
    user_id: UUID,
) -> Resume | None:
    result = await session.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_resumes_for_user(
    session: AsyncSession,
    *,
    user_id: UUID,
    limit: int,
    offset: int,
) -> tuple[list[Resume], int]:
    filters = Resume.user_id == user_id
    total = await session.scalar(select(func.count()).select_from(Resume).where(filters)) or 0
    result = await session.execute(
        select(Resume)
        .where(filters)
        .order_by(Resume.parsed_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all()), int(total)


# Re-export parser error for API mapping without importing parser internals.
__all__ = [
    "ResumeParseError",
    "ResumeTooLargeError",
    "create_parsed_resume",
    "get_resume_for_user",
    "list_resumes_for_user",
    "read_upload_limited",
    "sanitize_filename",
]
