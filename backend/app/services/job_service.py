from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    @staticmethod
    def create_job(db: Session, user_id: int, job_in: JobCreate) -> Job:
        job = Job(
            user_id=user_id,
            company=job_in.company,
            title=job_in.title,
            location=job_in.location,
            job_url=job_in.job_url,
            salary=job_in.salary,
            raw_jd_text=job_in.raw_jd_text,
            status="active",
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_job(db: Session, user_id: int, job_id: int) -> Optional[Job]:
        return db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()

    @staticmethod
    def list_jobs(db: Session, user_id: int, status_filter: Optional[str] = None) -> List[Job]:
        query = db.query(Job).filter(Job.user_id == user_id)
        if status_filter:
            query = query.filter(Job.status == status_filter)
        return query.order_by(Job.created_at.desc()).all()

    @classmethod
    def update_job(
        cls, db: Session, user_id: int, job_id: int, job_in: JobUpdate
    ) -> Optional[Job]:
        job = cls.get_job(db, user_id, job_id)
        if not job:
            return None
        update_data = job_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        db.commit()
        db.refresh(job)
        return job

    @classmethod
    def delete_job(cls, db: Session, user_id: int, job_id: int) -> bool:
        job = cls.get_job(db, user_id, job_id)
        if not job:
            return False
        db.delete(job)
        db.commit()
        return True


job_service = JobService()
