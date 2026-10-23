"""Create skills taxonomy and resume analyses.

Revision ID: 0003_skills_and_analyses
Revises: 0002_create_resumes
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_skills_and_analyses"
down_revision: Union[str, None] = "0002_create_resumes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("aliases", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "job_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_job_roles_slug"), "job_roles", ["slug"], unique=True)
    op.create_table(
        "job_role_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["job_role_id"], ["job_roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_role_id", "skill_id", name="uq_job_role_skill"),
    )
    op.create_index(
        op.f("ix_job_role_skills_job_role_id"),
        "job_role_skills",
        ["job_role_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_role_skills_skill_id"),
        "job_role_skills",
        ["skill_id"],
        unique=False,
    )
    op.create_table(
        "resume_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=80), nullable=False),
        sa.Column("matched_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("missing_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("extractor", sa.String(length=40), nullable=False),
        sa.Column(
            "analyzed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resume_id", "job_type", name="uq_resume_analysis_job_type"),
    )
    op.create_index(
        op.f("ix_resume_analyses_resume_id"),
        "resume_analyses",
        ["resume_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_resume_analyses_resume_id"), table_name="resume_analyses")
    op.drop_table("resume_analyses")
    op.drop_index(op.f("ix_job_role_skills_skill_id"), table_name="job_role_skills")
    op.drop_index(op.f("ix_job_role_skills_job_role_id"), table_name="job_role_skills")
    op.drop_table("job_role_skills")
    op.drop_index(op.f("ix_job_roles_slug"), table_name="job_roles")
    op.drop_table("job_roles")
    op.drop_table("skills")
