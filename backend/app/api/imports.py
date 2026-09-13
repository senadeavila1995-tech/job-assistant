from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.importers.computrabajo import import_computrabajo_jobs


router = APIRouter(prefix="/api/import", tags=["Imports"])


@router.post("/computrabajo")
def import_computrabajo(db: Session = Depends(get_db)):
    return import_computrabajo_jobs(db)
