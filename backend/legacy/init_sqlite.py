import asyncio
import os
import sys

# Ensure backend root directory is on sys.path so app module imports resolve correctly
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.models.base import Base
# Import all models to ensure they register with Base.metadata
import app.models.user
import app.models.resume
import app.models.skill
import app.models.course
import app.models.job


async def init_sqlite(db_file: str = "resume_portal.db"):
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in res.fetchall()]
        print(f"Database '{db_file}' initialized successfully!")
        print(f"Created tables ({len(tables)}): {', '.join(tables)}")

if __name__ == "__main__":
    asyncio.run(init_sqlite())
