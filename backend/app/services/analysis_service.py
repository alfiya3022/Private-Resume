from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.job import Job
from app.models.analysis import JobRequirement
from app.services.ai.ollama_provider import ollama_provider
from app.services.job_service import job_service


class AnalysisService:
    @staticmethod
    def get_analysis_by_job_id(
        db: Session, user_id: int, job_id: int
    ) -> Optional[JobRequirement]:
        """Fetches existing structured analysis for a job owned by candidate."""
        job = job_service.get_job(db, user_id=user_id, job_id=job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Target job not found"
            )
        return db.query(JobRequirement).filter(JobRequirement.job_id == job_id).first()

    @classmethod
    async def analyze_job(
        cls, db: Session, user_id: int, job_id: int
    ) -> JobRequirement:
        """Triggers local AI or deterministic requirement extraction and persists result."""
        job = job_service.get_job(db, user_id=user_id, job_id=job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Target job not found"
            )

        # Execute extraction through Ollama provider boundary
        structured = await ollama_provider.analyze_job_description(job.raw_jd_text)

        # Upsert JobRequirement record
        req = db.query(JobRequirement).filter(JobRequirement.job_id == job_id).first()
        if not req:
            req = JobRequirement(
                job_id=job_id,
                required_skills=structured.required_skills,
                preferred_skills=structured.preferred_skills,
                languages=structured.languages,
                frameworks=structured.frameworks,
                databases=structured.databases,
                tools=structured.tools,
                cloud=structured.cloud,
                responsibilities=structured.responsibilities,
                qualifications=structured.qualifications,
                experience_years=structured.experience_years,
                soft_skills=structured.soft_skills,
                raw_analysis=structured.model_dump(),
            )
            db.add(req)
        else:
            req.required_skills = structured.required_skills
            req.preferred_skills = structured.preferred_skills
            req.languages = structured.languages
            req.frameworks = structured.frameworks
            req.databases = structured.databases
            req.tools = structured.tools
            req.cloud = structured.cloud
            req.responsibilities = structured.responsibilities
            req.qualifications = structured.qualifications
            req.experience_years = structured.experience_years
            req.soft_skills = structured.soft_skills
            req.raw_analysis = structured.model_dump()

        db.commit()
        db.refresh(req)
        return req


analysis_service = AnalysisService()
