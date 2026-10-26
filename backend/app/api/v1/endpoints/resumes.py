from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.resume import MasterResume
from app.schemas.resume import (
    MasterResumeResponse,
    ResumeUploadQueuedResponse,
    ResumeStatusResponse,
    ParsedResumeResponse,
    ApplyExtractedDataRequest,
    ExtractedDataComparisonResponse,
)
from app.services.profile_service import profile_service
from app.services.pdf_service import pdf_service

router = APIRouter()


@router.post("", response_model=ResumeUploadQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_master_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    replace: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload master resume PDF and queue background extraction pipeline."""
    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported. DOCX, TXT, and scanned image formats are not accepted.",
        )

    resume = await profile_service.prepare_master_resume_upload(
        db=db, user_id=current_user.id, file=file, replace=replace
    )

    if not current_user.onboarding_completed:
        current_user.onboarding_completed = True
        db.commit()

    background_tasks.add_task(
        profile_service.process_master_resume_background,
        resume_id=resume.id,
        user_id=current_user.id,
    )

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "resume_id": resume.id,
            "filename": resume.filename,
            "file_size": resume.file_size,
            "parse_status": "queued",
            "message": "Resume upload accepted and queued for background extraction",
        },
    )


@router.get("/{resume_id}/status", response_model=ResumeStatusResponse)
def get_resume_status(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve current background parsing status and stage for a resume."""
    resume = db.query(MasterResume).filter(
        MasterResume.id == resume_id, MasterResume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Master resume not found"
        )

    return {
        "resume_id": resume.id,
        "parse_status": resume.parse_status or "complete",
        "parse_stage": resume.parse_stage or ("Complete" if resume.parse_status == "complete" else "Queued"),
        "parse_error": resume.parse_error,
    }


@router.get("", response_model=List[MasterResumeResponse])
def get_user_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all uploaded master resumes for the authenticated candidate."""
    return profile_service.get_user_resumes(db, current_user.id)


@router.get("/{resume_id}/extracted-data", response_model=ExtractedDataComparisonResponse)
def get_resume_extracted_data(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve structured extraction details and comparison with candidate profile."""
    return profile_service.get_resume_extracted_data(db, current_user.id, resume_id)


@router.post("/{resume_id}/apply-to-profile", response_model=Dict[str, Any])
def apply_extracted_data_to_profile(
    resume_id: int,
    request: ApplyExtractedDataRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Selectively apply approved extracted sections from master resume to candidate profile."""
    return profile_service.apply_extracted_data_to_profile(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
        sections=request.sections,
        overwrite_existing=request.overwrite_existing,
        edited_data=request.edited_data,
        item_decisions=request.item_decisions,
        remember_corrections=request.remember_corrections,
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a master resume record and its stored PDF artifact."""
    success = profile_service.delete_resume(db, current_user.id, resume_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Master resume not found"
        )
