# Legacy (not active)

This folder holds code from an **earlier authenticated / SQLAlchemy / Alembic** experiment.

It is **not imported** by the active CareerCratly.AI FastAPI app (`app/main.py` → `app/api/router.py`).

## Why it is kept

Preserved for reference if you later reintroduce:

- JWT candidate/recruiter accounts  
- PostgreSQL / SQLite ORM persistence  
- Alembic migrations  

## Do not

- Import these modules into `app/` without a deliberate migration plan  
- Treat this as production-ready auth  

## Contents

| Path | Origin |
|------|--------|
| `api/` | Auth routes and DB dependencies |
| `services/` | JWT auth, ORM resume/jobs, old recommenders |
| `schemas/` | Auth / application schemas |
| `models/` | SQLAlchemy `User`, `Skill`, `Base` |
| `db/` | Async SQLAlchemy session + seed helpers |
| `alembic/` | Historical migrations |
| `core/` | JWT helpers and SlowAPI limiter |

## Active stack instead

- In-memory resume store  
- JSON catalogs under `app/data/`  
- Job providers under `app/providers/jobs/`  
- No authentication  
