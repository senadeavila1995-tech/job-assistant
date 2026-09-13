from app.importers.job_importer import JobData, import_job


COMPUTRABAJO_JOBS = [
    JobData(
        title="Desarrollador/a Full Stack SaaS - React + Next.js + Node.js + TypeScript",
        company="DEV LAB TECHNOLOGIES S.A.S",
        source="Computrabajo",
        url="https://co.computrabajo.com/ofertas-de-trabajo/oferta-de-trabajo-de-desarrolladora-full-stack-saas-react-nextjs-nodejs-typescript-en-neiva-6F9F1FDBBD58FE6C61373E686DCF3405",
        description=(
            "Desarrollo Full Stack para plataforma SaaS. "
            "React, Next.js, Node.js, TypeScript, JavaScript, "
            "REST, MySQL, SQL, Git, GitHub y Docker."
        ),
        salary=None,
        remote=True,
        location="Colombia",
        contract_type=None,
        workday="Tiempo completo",
        experience=None,
        education=None,
        requirements=(
            "Desarrollo de aplicaciones Full Stack para plataforma SaaS."
        ),
        skills=(
            "React, Next.js, Node.js, TypeScript, JavaScript, "
            "REST, MySQL, SQL, Git, GitHub, Docker"
        ),
        keywords=(
            "Full Stack, SaaS, React, Next.js, Node.js, "
            "TypeScript, JavaScript, REST, MySQL"
        ),
    ),

    JobData(
        title="Desarrollador Backend (Python)",
        company="Accenture LTDA",
        source="Computrabajo",
        url="https://co.computrabajo.com/ofertas-de-trabajo/oferta-de-trabajo-de-python-backend-developer-r-d-remote-work-ref-0071e-rd-en--B81F4374811AFDAF61373E686DCF3405",
        description=(
            "Desarrollo Backend con Python. "
            "Oferta orientada a desarrollo de software backend."
        ),
        salary=None,
        remote=True,
        location="Colombia",
        contract_type=None,
        workday="Tiempo completo",
        experience=None,
        education=None,
        requirements=(
            "Desarrollo de software backend utilizando Python."
        ),
        skills="Python, Backend",
        keywords="Backend, Python, Software Developer",
    ),
]


def import_computrabajo_jobs(db):
    imported = 0
    duplicated = 0
    skipped = 0
    jobs = []

    for data in COMPUTRABAJO_JOBS:
        job, created = import_job(db, data)

        if job is None:
            skipped += 1
            continue

        if created:
            imported += 1
        else:
            duplicated += 1

        jobs.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "source": job.source,
            "salary": job.salary,
            "remote": job.remote,
            "published_at": job.published_at,
            "last_seen_at": job.last_seen_at,
            "contract_type": job.contract_type,
            "workday": job.workday,
            "experience": job.experience,
            "education": job.education,
            "url": job.url,
            "created": created,
        })

    return {
        "source": "Computrabajo",
        "imported": imported,
        "duplicated": duplicated,
        "skipped": skipped,
        "total": len(COMPUTRABAJO_JOBS),
        "jobs": jobs,
    }
