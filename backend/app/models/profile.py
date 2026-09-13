from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profile"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    target_role: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    salary_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    experience_years: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    remote_preferred: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    profile_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    skill: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    job_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    skill: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
