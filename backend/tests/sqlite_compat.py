"""Make PostgreSQL-specific SQLAlchemy types compile on SQLite for tests."""

from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(_type, compiler, **_kw) -> str:
    return "JSON"


@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(_type, compiler, **_kw) -> str:
    return "CHAR(36)"
