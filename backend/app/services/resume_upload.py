from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile, status

from app.core.config import settings
from app.core.exceptions import AppError
from app.services.resume_parser import ResumeParseError, parse_resume
from app.services.resume_store import resume_store
from app.services.skill_extractor import get_skill_extractor
from app.services.storage import get_storage_service

_PARSE_STATUS = {
    "unsupported_type": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    "corrupt_file": status.HTTP_422_UNPROCESSABLE_ENTITY,
    "empty_text": status.HTTP_422_UNPROCESSABLE_ENTITY,
    "empty_file": status.HTTP_400_BAD_REQUEST,
    "parse_error": status.HTTP_422_UNPROCESSABLE_ENTITY,
}


class ResumeTooLargeError(Exception):
    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes
        super().__init__(f"File exceeds the {max_bytes} byte limit")


def sanitize_filename(filename: str | None) -> str:
    name = Path(filename or "resume").name.strip().replace("\x00", "")
    if name in {"", ".", ".."}:
        name = "resume"
    return name[:255]


async def read_upload_limited(file: UploadFile, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ResumeTooLargeError(max_bytes)
        chunks.append(chunk)
    return b"".join(chunks)


async def upload_and_parse(file: UploadFile) -> dict:
    try:
        file_bytes = await read_upload_limited(file, settings.max_resume_size_bytes)
    except ResumeTooLargeError as exc:
        raise AppError(
            f"File exceeds the {exc.max_bytes} byte (5MB) limit",
            code="payload_too_large",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details={"max_bytes": exc.max_bytes},
        ) from None
    finally:
        await file.close()

    safe_name = sanitize_filename(file.filename)
    try:
        parsed = parse_resume(file_bytes, safe_name)
    except ResumeParseError as exc:
        raise AppError(
            str(exc),
            code=exc.code,
            status_code=_PARSE_STATUS.get(exc.code, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ) from None

    stored = resume_store.save(
        filename=parsed["filename"],
        file_type=parsed["file_type"],
        text=parsed["text"],
        pages=parsed["pages"],
        metadata=parsed["metadata"],
    )
    storage_key = f"{stored.id}{Path(safe_name).suffix.lower()}"
    await get_storage_service().save(file_bytes, storage_key)

    skills = get_skill_extractor().extract(parsed["text"])
    return {
        "resume_id": stored.id,
        "filename": stored.filename,
        "file_type": stored.file_type,
        "text": stored.text,
        "pages": stored.pages,
        "metadata": stored.metadata,
        "extracted_skills": skills,
    }
