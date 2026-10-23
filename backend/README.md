# CareerCratly.AI — Backend

FastAPI service for resume upload/analysis, job search (provider architecture), courses, project resources, and interview Q&A.

For full setup instructions, see the [root README](../README.md).

## Quick start

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/api/health  

## Tests

```powershell
pytest -q
```

## Legacy code

Unused auth/SQLAlchemy/Alembic experiments live in [`legacy/`](./legacy/) and are **not** wired into the running API.
