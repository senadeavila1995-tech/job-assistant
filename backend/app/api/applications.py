from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.application import Application
from app.models.job import Job
from app.models.match import JobMatch


router = APIRouter(
    prefix="/api/applications",
    tags=["Applications"],
)


def serialize_application(
    application: Application,
    job: Job | None,
    match: JobMatch | None,
):
    return {
        "id": application.id,
        "job_id": application.job_id,
        "source": application.source,
        "application_url": application.application_url,
        "applied_at": application.applied_at,
        "created_at": application.created_at,
        "job": {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "source": job.source,
            "url": job.url,
            "salary": job.salary,
            "remote": job.remote,
        } if job else None,
        "match": {
            "score": match.score,
            "recommendation": match.recommendation,
            "skill_score": match.skill_score,
            "salary_score": match.salary_score,
            "remote_score": match.remote_score,
        } if match else None,
    }


@router.post("/{job_id}")
def mark_as_applied(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Oferta no encontrada",
        )

    existing = db.scalars(
        select(Application).where(
            Application.job_id == job_id
        )
    ).first()

    if existing:
        return serialize_application(
            existing,
            job,
            get_job_match(db, job_id),
        )

    application = Application(
        job_id=job.id,
        source=job.source,
        application_url=job.url,
        applied_at=datetime.utcnow(),
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return serialize_application(
        application,
        job,
        get_job_match(db, job_id),
    )


@router.get("")
def list_applications(
    db: Session = Depends(get_db),
):
    applications = db.scalars(
        select(Application)
        .order_by(Application.applied_at.desc())
    ).all()

    result = []

    for application in applications:
        job = db.get(Job, application.job_id)

        result.append(
            serialize_application(
                application,
                job,
                get_job_match(db, application.job_id),
            )
        )

    return result


@router.get("/{job_id}")
def get_application_by_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    application = db.scalars(
        select(Application).where(
            Application.job_id == job_id
        )
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="La oferta todavía no está marcada como aplicada",
        )

    job = db.get(Job, job_id)

    return serialize_application(
        application,
        job,
        get_job_match(db, job_id),
    )


@router.delete("/{job_id}")
def unmark_as_applied(
    job_id: int,
    db: Session = Depends(get_db),
):
    application = db.scalars(
        select(Application).where(
            Application.job_id == job_id
        )
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="La oferta no está marcada como aplicada",
        )

    db.delete(application)
    db.commit()

    return {
        "ok": True,
        "message": "Oferta desmarcada como aplicada",
        "job_id": job_id,
    }


def get_job_match(
    db: Session,
    job_id: int,
):
    return db.scalars(
        select(JobMatch)
        .where(JobMatch.job_id == job_id)
        .order_by(JobMatch.score.desc())
    ).first()
