from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, profile, resumes, jobs, tailored_resumes, applications

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["Master Resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(tailored_resumes.router, prefix="/tailored-resumes", tags=["Tailored Resumes"])
api_router.include_router(applications.router, prefix="/applications", tags=["Applications"])




