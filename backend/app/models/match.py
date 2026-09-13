from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    job_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    profile_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    skill_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    salary_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    remote_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    matched_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    missing_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommendation: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
