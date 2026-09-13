from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.profile import CandidateProfile, CandidateSkill

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"],
)


@router.get("")
def get_profile(db: Session = Depends(get_db)):
    profile = db.scalars(
        select(CandidateProfile)
        .order_by(CandidateProfile.id.desc())
    ).first()

    if not profile:
        return None

    skills = db.scalars(
        select(CandidateSkill)
        .where(CandidateSkill.profile_id == profile.id)
        .order_by(CandidateSkill.skill)
    ).all()

    return {
        "id": profile.id,
        "name": profile.name,
        "target_role": profile.target_role,
        "salary_min": profile.salary_min,
        "experience_years": profile.experience_years,
        "remote_preferred": profile.remote_preferred,
        "summary": profile.summary,
        "skills": [
            skill.skill
            for skill in skills
        ],
    }


@router.post("")
def create_profile(
    db: Session = Depends(get_db),
):
    existing = db.scalars(
        select(CandidateProfile)
    ).first()

    if existing:
        return get_profile(db)

    profile = CandidateProfile(
        name="Jesús Daniel de Ávila Niebles",
        target_role="Junior Full Stack Web Developer",
        salary_min=4000000,
        experience_years=None,
        remote_preferred=True,
        summary=(
            "Desarrollador de software con formación técnica en programación "
            "y experiencia práctica en desarrollo Full Stack y Backend. "
            "Experiencia construyendo APIs REST, sistemas POS multiempresa, "
            "marketplaces y soluciones con Node.js, TypeScript, React, "
            "MySQL, SQL, MongoDB, .NET, C#, Python y FastAPI. "
            "Manejo de JWT, Git, GitHub y desarrollo de aplicaciones web."
        ),
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    skills = [
        "Node.js",
        "Express",
        "TypeScript",
        "JavaScript",
        "React",
        "Angular",
        "Python",
        "FastAPI",
        "MySQL",
        "SQL",
        "MongoDB",
        ".NET",
        "C#",
        "REST API",
        "JWT",
        "Git",
        "GitHub",
        "Bootstrap",
        "PHP",
        "Power BI",
    ]

    for skill_name in skills:
        db.add(
            CandidateSkill(
                profile_id=profile.id,
                skill=skill_name,
            )
        )

    db.commit()

    return get_profile(db)


@router.delete("/skills")
def clear_skills(
    db: Session = Depends(get_db),
):
    profile = db.scalars(
        select(CandidateProfile)
        .order_by(CandidateProfile.id.desc())
    ).first()

    if not profile:
        return {
            "ok": False,
            "message": "No existe perfil",
        }

    db.execute(
        delete(CandidateSkill).where(
            CandidateSkill.profile_id == profile.id
        )
    )

    db.commit()

    return {
        "ok": True,
        "message": "Habilidades eliminadas",
    }
