import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.job import Job
from app.models.match import JobMatch
from app.services.matching import calculate_match, get_profile


router = APIRouter(
    prefix="/api/matches",
    tags=["Matches"],
)


def save_match(
    db: Session,
    result: dict,
) -> JobMatch:
    existing = db.scalars(
        select(JobMatch)
        .where(JobMatch.job_id == result["job_id"])
        .where(JobMatch.profile_id == result["profile_id"])
    ).first()

    if existing:
        match = existing
    else:
        match = JobMatch(
            job_id=result["job_id"],
            profile_id=result["profile_id"],
        )
        db.add(match)

    match.score = result["score"]
    match.skill_score = result["skill_score"]
    match.salary_score = result["salary_score"]
    match.remote_score = result["remote_score"]
    match.matched_skills = json.dumps(
        result["matched_skills"],
        ensure_ascii=False,
    )
    match.missing_skills = json.dumps(
        result["missing_skills"],
        ensure_ascii=False,
    )
    match.recommendation = result["recommendation"]

    return match


@router.get("/job/{job_id}")
def match_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Oferta no encontrada",
        )

    profile = get_profile(db)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil candidato no encontrado",
        )

    result = calculate_match(
        db,
        job,
        profile,
    )

    match = save_match(
        db,
        result,
    )

    db.commit()
    db.refresh(match)

    return result


@router.get("")
def list_matches(
    db: Session = Depends(get_db),
):
    profile = get_profile(db)

    if not profile:
        return []

    jobs = db.scalars(
        select(Job).order_by(Job.id.desc())
    ).all()

    results = []

    for job in jobs:
        result = calculate_match(
            db,
            job,
            profile,
        )

        save_match(
            db,
            result,
        )

        results.append(result)

    db.commit()

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )
