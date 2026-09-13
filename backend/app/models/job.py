from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    company: Mapped[str] = mapped_column(String(255), nullable=False)

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source: Mapped[str] = mapped_column(String(100), nullable=False)

    url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    url_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    salary: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    remote: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    contract_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    workday: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    experience: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    education: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    keywords: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
