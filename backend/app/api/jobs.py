from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.job import Job

router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
)


@router.get("")
def list_jobs(
    db: Session = Depends(get_db),
):
    jobs = db.scalars(
        select(Job)
        .where(
            Job.remote.is_(True),
            Job.is_active.is_(True),
        )
        .order_by(
            Job.published_at.desc(),
            Job.last_seen_at.desc(),
            Job.id.desc(),
        )
    ).all()

    return jobs


@router.post("")
def create_job(
    title: str,
    company: str,
    source: str,
    url: str | None = None,
    description: str | None = None,
    salary: str | None = None,
    remote: bool = False,
    location: str | None = None,
    db: Session = Depends(get_db),
):
    if not remote:
        return {
            "ok": False,
            "message": "El sistema solo admite ofertas 100% remotas.",
        }

    job = Job(
        title=title,
        company=company,
        source=source,
        url=url,
        description=description,
        salary=salary,
        remote=True,
        location=location,
        is_active=True,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job
