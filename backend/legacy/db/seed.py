from __future__ import annotations

import uuid

from sqlalchemy import delete, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.loader import load_courses, load_job_roles, load_skills
from app.models.course import Course, CourseLevel
from app.models.skill import JobRole, JobRoleSkill, Skill


def _stable_id(kind: str, key: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_URL, f"resume-portal:{kind}:{key.lower()}")


async def seed_taxonomy(session: AsyncSession) -> None:
    """Upsert master skills and job-role weights from JSON into Postgres."""
    skills = load_skills()
    if skills:
        skill_rows = [
            {
                "id": _stable_id("skill", item["name"]),
                "name": item["name"],
                "aliases": item.get("aliases") or [],
            }
            for item in skills
        ]
        stmt = insert(Skill).values(skill_rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Skill.name],
            set_={"aliases": stmt.excluded.aliases},
        )
        await session.execute(stmt)

    name_to_id = {
        item["name"]: _stable_id("skill", item["name"]) for item in skills
    }

    roles = load_job_roles()
    if roles:
        role_rows = [
            {
                "id": _stable_id("role", role["slug"]),
                "slug": role["slug"],
                "name": role["name"],
            }
            for role in roles
        ]
        stmt = insert(JobRole).values(role_rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[JobRole.slug],
            set_={"name": stmt.excluded.name},
        )
        await session.execute(stmt)

    await session.execute(delete(JobRoleSkill))
    link_rows: list[dict] = []
    for role in roles:
        role_id = _stable_id("role", role["slug"])
        for required in role.get("skills") or []:
            skill_id = name_to_id.get(required["name"])
            if skill_id is None:
                continue
            link_rows.append(
                {
                    "id": _stable_id("link", f"{role['slug']}:{required['name']}"),
                    "job_role_id": role_id,
                    "skill_id": skill_id,
                    "weight": float(required["weight"]),
                }
            )
    if link_rows:
        await session.execute(insert(JobRoleSkill).values(link_rows))

    await session.commit()
    await seed_courses(session)


async def seed_courses(session: AsyncSession) -> None:
    courses = load_courses()
    if not courses:
        return

    rows = []
    for item in courses:
        rows.append(
            {
                "id": _stable_id("course", item["url"]),
                "title": item["title"],
                "provider": item["provider"],
                "url": item["url"],
                "skill_tag": item["skill_tag"],
                "level": CourseLevel(item["level"]),
            }
        )
    stmt = insert(Course).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Course.url],
        set_={
            "title": stmt.excluded.title,
            "provider": stmt.excluded.provider,
            "skill_tag": stmt.excluded.skill_tag,
            "level": stmt.excluded.level,
        },
    )
    await session.execute(stmt)
    await session.commit()


async def get_job_role_by_type(session: AsyncSession, job_type: str) -> JobRole | None:
    key = job_type.strip()
    slug = key.lower().replace(" ", "_").replace("-", "_")
    result = await session.execute(
        select(JobRole)
        .options(selectinload(JobRole.skill_links).selectinload(JobRoleSkill.skill))
        .where(or_(JobRole.slug == slug, JobRole.name.ilike(key)))
    )
    return result.scalar_one_or_none()


async def list_job_roles(session: AsyncSession) -> list[JobRole]:
    result = await session.execute(select(JobRole).order_by(JobRole.name))
    return list(result.scalars().all())
