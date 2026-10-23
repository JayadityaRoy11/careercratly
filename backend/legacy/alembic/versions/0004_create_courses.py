"""Create courses table.

Revision ID: 0004_create_courses
Revises: 0003_skills_and_analyses
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_create_courses"
down_revision: Union[str, None] = "0003_skills_and_analyses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

course_level_enum = postgresql.ENUM(
    "beginner",
    "intermediate",
    "advanced",
    name="course_level",
)


def upgrade() -> None:
    course_level_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("skill_tag", sa.String(length=120), nullable=False),
        sa.Column(
            "level",
            postgresql.ENUM(
                "beginner",
                "intermediate",
                "advanced",
                name="course_level",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index(op.f("ix_courses_skill_tag"), "courses", ["skill_tag"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_courses_skill_tag"), table_name="courses")
    op.drop_table("courses")
    course_level_enum.drop(op.get_bind(), checkfirst=True)
