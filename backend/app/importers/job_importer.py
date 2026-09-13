from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job


@dataclass
class JobData:
    title: str
    company: str
    source: str

    url: str | None = None
    description: str | None = None
    salary: str | None = None
    remote: bool = False

    location: str | None = None
    published_at: datetime | None = None
    contract_type: str | None = None
    workday: str | None = None
    experience: str | None = None
    education: str | None = None
    requirements: str | None = None
    skills: str | None = None
    keywords: str | None = None


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    value = " ".join(value.strip().split())

    return value or None


def normalize_job(data: JobData) -> JobData:
    return JobData(
        title=normalize_text(data.title) or "",
        company=normalize_text(data.company) or "",
        source=normalize_text(data.source) or "",
        url=normalize_text(data.url),
        description=normalize_text(data.description),
        salary=normalize_text(data.salary),
        remote=bool(data.remote),
        location=normalize_text(data.location),
        published_at=data.published_at,
        contract_type=normalize_text(data.contract_type),
        workday=normalize_text(data.workday),
        experience=normalize_text(data.experience),
        education=normalize_text(data.education),
        requirements=normalize_text(data.requirements),
        skills=normalize_text(data.skills),
        keywords=normalize_text(data.keywords),
    )


def generate_url_hash(url: str | None) -> str | None:
    if not url:
        return None

    return sha256(url.encode("utf-8")).hexdigest()


def get_existing_job(
    db: Session,
    url_hash: str | None,
) -> Job | None:
    if not url_hash:
        return None

    return db.scalars(
        select(Job).where(Job.url_hash == url_hash)
    ).first()


def update_existing_job(
    job: Job,
    data: JobData,
) -> Job:
    job.title = data.title
    job.company = data.company
    job.source = data.source
    job.url = data.url
    job.description = data.description
    job.salary = data.salary
    job.remote = data.remote
    job.location = data.location
    job.published_at = data.published_at
    job.contract_type = data.contract_type
    job.workday = data.workday
    job.experience = data.experience
    job.education = data.education
    job.requirements = data.requirements
    job.skills = data.skills
    job.keywords = data.keywords
    job.last_seen_at = datetime.utcnow()
    job.is_active = True

    return job


def import_job(
    db: Session,
    data: JobData,
) -> tuple[Job | None, bool]:

    data = normalize_job(data)

    # Este sistema solo acepta ofertas 100% remotas.
    if not data.remote:
        return None, False

    url_hash = generate_url_hash(data.url)

    existing = get_existing_job(db, url_hash)

    if existing:
        update_existing_job(existing, data)

        db.commit()
        db.refresh(existing)

        return existing, False

    job = Job(
        title=data.title,
        company=data.company,
        source=data.source,
        url=data.url,
        url_hash=url_hash,
        description=data.description,
        salary=data.salary,
        remote=data.remote,
        location=data.location,
        published_at=data.published_at,
        last_seen_at=datetime.utcnow(),
        contract_type=data.contract_type,
        workday=data.workday,
        experience=data.experience,
        education=data.education,
        requirements=data.requirements,
        skills=data.skills,
        keywords=data.keywords,
        is_active=True,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job, True
