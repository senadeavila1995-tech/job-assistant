import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.profile import CandidateProfile, CandidateSkill


SKILL_ALIASES = {
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "typescript": "typescript",
    "javascript": "javascript",
    "react": "react",
    "angular": "angular",
    "express": "express",
    "mysql": "mysql",
    "sql": "sql",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "python": "python",
    "fastapi": "fastapi",
    ".net": ".net",
    "dotnet": ".net",
    "c#": "c#",
    "rest": "rest api",
    "rest api": "rest api",
    "api rest": "rest api",
    "jwt": "jwt",
    "git": "git",
    "github": "github",
    "php": "php",
    "power bi": "power bi",
    "bootstrap": "bootstrap",
    "docker": "docker",
    "aws": "aws",
    "azure": "azure",
}


def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def canonical_skill(value: str) -> str:
    value = normalize(value)
    return SKILL_ALIASES.get(value, value)


def get_profile(db: Session) -> CandidateProfile | None:
    return db.scalars(
        select(CandidateProfile)
        .order_by(CandidateProfile.id.desc())
    ).first()


def get_candidate_skills(
    db: Session,
    profile_id: int,
) -> set[str]:
    skills = db.scalars(
        select(CandidateSkill)
        .where(CandidateSkill.profile_id == profile_id)
    ).all()

    return {
        canonical_skill(skill.skill)
        for skill in skills
    }


def extract_job_skills(job: Job) -> set[str]:
    text = normalize(
        f"{job.title or ''} {job.description or ''}"
    )

    found = set()

    for alias, canonical in SKILL_ALIASES.items():
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"

        if re.search(pattern, text):
            found.add(canonical)

    return found


def calculate_skill_score(
    candidate_skills: set[str],
    job_skills: set[str],
) -> tuple[float, list[str], list[str]]:
    if not job_skills:
        return 50.0, [], []

    matched = sorted(candidate_skills.intersection(job_skills))
    missing = sorted(job_skills.difference(candidate_skills))

    score = (len(matched) / len(job_skills)) * 100

    return round(score, 2), matched, missing


def calculate_role_score(
    profile: CandidateProfile,
    job: Job,
) -> float:
    target = normalize(profile.target_role or "")
    title = normalize(job.title or "")
    description = normalize(job.description or "")

    if not target:
        return 50.0

    text = f"{title} {description}"

    target_full_stack = (
        "full stack" in target
        or "fullstack" in target
    )

    target_backend = (
        "backend" in target
        or "back end" in target
    )

    target_frontend = (
        "frontend" in target
        or "front end" in target
    )

    job_backend = (
        "backend" in text
        or "back end" in text
        or "back-end" in text
    )

    job_frontend = (
        "frontend" in text
        or "front end" in text
        or "front-end" in text
    )

    job_full_stack = (
        "full stack" in text
        or "fullstack" in text
    )

    job_developer = (
        "developer" in text
        or "desarrollador" in text
        or "software engineer" in text
        or "ingeniero de software" in text
    )

    if target_full_stack:
        if job_full_stack:
            return 100.0

        if job_backend or job_frontend:
            return 95.0

        if job_developer:
            return 80.0

    if target_backend:
        if job_backend:
            return 100.0

        if job_full_stack:
            return 90.0

        if job_developer:
            return 75.0

    if target_frontend:
        if job_frontend:
            return 100.0

        if job_full_stack:
            return 90.0

        if job_developer:
            return 75.0

    if job_developer:
        return 70.0

    return 30.0

def parse_salary(value: str | None) -> int | None:
    if not value:
        return None

    numbers = re.findall(r"\d[\d.,]*", value)

    if not numbers:
        return None

    cleaned = numbers[0].replace(".", "").replace(",", "")

    try:
        return int(cleaned)
    except ValueError:
        return None


def calculate_salary_score(
    profile: CandidateProfile,
    job: Job,
) -> float:
    minimum = profile.salary_min
    offered = parse_salary(job.salary)

    if not minimum or not offered:
        return 50.0

    if offered >= minimum:
        return 100.0

    percentage = (offered / minimum) * 100

    return round(
        max(0.0, min(100.0, percentage)),
        2,
    )


def calculate_remote_score(
    profile: CandidateProfile,
    job: Job,
) -> float:
    if not profile.remote_preferred:
        return 100.0

    return 100.0 if job.remote else 0.0


def calculate_match(
    db: Session,
    job: Job,
    profile: CandidateProfile,
) -> dict:
    candidate_skills = get_candidate_skills(
        db,
        profile.id,
    )

    job_skills = extract_job_skills(job)

    skill_score, matched, missing = calculate_skill_score(
        candidate_skills,
        job_skills,
    )

    role_score = calculate_role_score(
        profile,
        job,
    )

    salary_score = calculate_salary_score(
        profile,
        job,
    )

    remote_score = calculate_remote_score(
        profile,
        job,
    )

    score = (
        skill_score * 0.35
        + role_score * 0.20
        + salary_score * 0.15
        + remote_score * 0.10
        + 20.0
    )

    score = round(
        min(100.0, score),
        2,
    )

    if score >= 80:
        recommendation = "RECOMENDADA"
    elif score >= 60:
        recommendation = "REVISAR"
    else:
        recommendation = "DESCARTADA"

    return {
        "job_id": job.id,
        "profile_id": profile.id,
        "score": score,
        "skill_score": skill_score,
        "role_score": role_score,
        "salary_score": salary_score,
        "remote_score": remote_score,
        "job_skills": sorted(job_skills),
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendation": recommendation,
    }
