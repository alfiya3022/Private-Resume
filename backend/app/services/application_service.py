from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.user import User
from app.models.job import Job
from app.models.tailored_resume import TailoredResume
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationService:
    def create_application(
        self, db: Session, user: User, data: ApplicationCreate
    ) -> Application:
        # Verify job belongs to user
        job = db.query(Job).filter(Job.id == data.job_id, Job.user_id == user.id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target job not found or unauthorized",
            )

        # Verify tailored resume if provided
        if data.tailored_resume_id:
            resume = db.query(TailoredResume).filter(
                TailoredResume.id == data.tailored_resume_id,
                TailoredResume.user_id == user.id,
            ).first()
            if not resume:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tailored resume version not found or unauthorized",
                )

        # Create application record
        app_record = Application(
            user_id=user.id,
            job_id=data.job_id,
            tailored_resume_id=data.tailored_resume_id,
            status=data.status or "applied",
            notes=data.notes,
        )

        # Optionally update job status to reflect application
        if data.status in ["applied", "interviewing", "offer", "rejected"]:
            job.status = data.status

        db.add(app_record)
        db.commit()
        db.refresh(app_record)
        return app_record

    def list_applications(
        self, db: Session, user: User, status_filter: Optional[str] = None
    ) -> List[Application]:
        query = (
            db.query(Application)
            .options(joinedload(Application.job), joinedload(Application.tailored_resume))
            .filter(Application.user_id == user.id)
        )
        if status_filter:
            query = query.filter(Application.status == status_filter)
        return query.order_by(Application.created_at.desc()).all()

    def get_application(
        self, db: Session, user: User, application_id: int
    ) -> Application:
        app_record = (
            db.query(Application)
            .options(joinedload(Application.job), joinedload(Application.tailored_resume))
            .filter(Application.id == application_id, Application.user_id == user.id)
            .first()
        )
        if not app_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or access unauthorized",
            )
        return app_record

    def update_application(
        self, db: Session, user: User, application_id: int, data: ApplicationUpdate
    ) -> Application:
        app_record = self.get_application(db, user, application_id)
        
        if data.status is not None:
            app_record.status = data.status
            # Keep parent Job status in sync
            if app_record.job and data.status in ["applied", "interviewing", "offer", "rejected"]:
                app_record.job.status = data.status

        if data.notes is not None:
            app_record.notes = data.notes

        db.commit()
        db.refresh(app_record)
        return app_record

    def delete_application(
        self, db: Session, user: User, application_id: int
    ) -> None:
        app_record = self.get_application(db, user, application_id)
        db.delete(app_record)
        db.commit()


application_service = ApplicationService()
