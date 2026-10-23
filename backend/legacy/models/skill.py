import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    aliases: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    job_links: Mapped[list["JobRoleSkill"]] = relationship(back_populates="skill")


class JobRole(Base):
    __tablename__ = "job_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    skill_links: Mapped[list["JobRoleSkill"]] = relationship(
        back_populates="job_role",
        cascade="all, delete-orphan",
    )


class JobRoleSkill(Base):
    __tablename__ = "job_role_skills"
    __table_args__ = (UniqueConstraint("job_role_id", "skill_id", name="uq_job_role_skill"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)

    job_role: Mapped[JobRole] = relationship(back_populates="skill_links")
    skill: Mapped[Skill] = relationship(back_populates="job_links")


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"
    __table_args__ = (
        UniqueConstraint("resume_id", "job_type", name="uq_resume_analysis_job_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_type: Mapped[str] = mapped_column(String(80), nullable=False)
    matched_skills: Mapped[list] = mapped_column(JSON, nullable=False)
    missing_skills: Mapped[list] = mapped_column(JSON, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    extractor: Mapped[str] = mapped_column(String(40), nullable=False)
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    resume: Mapped["Resume"] = relationship(back_populates="analyses")
