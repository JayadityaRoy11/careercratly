from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from uuid import UUID, uuid4
from typing import Any


@dataclass
class StoredResume:
    id: UUID
    filename: str
    file_type: str
    text: str
    pages: int
    metadata: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class InMemoryResumeStore:
    def __init__(self) -> None:
        self._items: dict[UUID, StoredResume] = {}
        self._lock = Lock()

    def save(
        self,
        *,
        filename: str,
        file_type: str,
        text: str,
        pages: int,
        metadata: dict[str, Any],
    ) -> StoredResume:
        record = StoredResume(
            id=uuid4(),
            filename=filename,
            file_type=file_type,
            text=text,
            pages=pages,
            metadata=metadata,
        )
        with self._lock:
            self._items[record.id] = record
        return record

    def get(self, resume_id: UUID) -> StoredResume | None:
        with self._lock:
            return self._items.get(resume_id)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


resume_store = InMemoryResumeStore()
