from app.models.database import Base, engine
from app.models.job import Job
from app.models.profile import CandidateProfile, CandidateSkill, JobSkill
from app.models.match import JobMatch
from app.models.application import Application


def create_tables():
    Base.metadata.create_all(bind=engine)
