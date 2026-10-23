"""File storage backends. Local disk now; S3 can implement the same protocol later."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import settings


class StorageService(ABC):
    @abstractmethod
    async def save(self, data: bytes, key: str) -> str:
        """Persist bytes at `key` and return the stored key."""

    @abstractmethod
    async def read(self, key: str) -> bytes:
        """Return file bytes for `key`."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove `key` if it exists."""


class LocalStorageService(StorageService):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Invalid storage key")
        return path

    async def save(self, data: bytes, key: str) -> str:
        path = self._resolve(key)

        def _write() -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        await asyncio.to_thread(_write)
        return key

    async def read(self, key: str) -> bytes:
        path = self._resolve(key)
        return await asyncio.to_thread(path.read_bytes)

    async def delete(self, key: str) -> None:
        path = self._resolve(key)

        def _delete() -> None:
            if path.exists():
                path.unlink()

        await asyncio.to_thread(_delete)


class S3StorageService(StorageService):
    """Placeholder for a future S3-backed implementation."""

    async def save(self, data: bytes, key: str) -> str:
        raise NotImplementedError("S3 storage is not implemented yet")

    async def read(self, key: str) -> bytes:
        raise NotImplementedError("S3 storage is not implemented yet")

    async def delete(self, key: str) -> None:
        raise NotImplementedError("S3 storage is not implemented yet")


def get_storage_service() -> StorageService:
    backend = settings.storage_backend.lower()
    if backend == "local":
        return LocalStorageService(settings.upload_dir)
    if backend == "s3":
        return S3StorageService()
    raise ValueError(f"Unknown storage backend: {settings.storage_backend}")
