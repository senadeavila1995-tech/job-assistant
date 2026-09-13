from fastapi import FastAPI

from app.api.jobs import router as jobs_router
from app.api.profile import router as profile_router
from app.api.matches import router as matches_router
from app.api.applications import router as applications_router
from app.api.imports import router as imports_router
from app.models import create_tables


app = FastAPI(
    title="Job Assistant API",
    description="Asistente inteligente para analizar y gestionar oportunidades laborales",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    create_tables()


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "service": "job-assistant",
        "version": "0.1.0",
    }


app.include_router(jobs_router)
app.include_router(profile_router)
app.include_router(matches_router)
app.include_router(applications_router)
app.include_router(imports_router)
