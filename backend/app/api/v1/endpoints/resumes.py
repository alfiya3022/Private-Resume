from typing import List, Dict, Any
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.resume import (
    MasterResumeResponse,
    ParsedResumeResponse,
    ApplyExtractedDataRequest,
    ExtractedDataComparisonResponse,
)
from app.services.profile_service import profile_service
from app.services.pdf_service import pdf_service

router = APIRouter()


@router.post("", response_model=ParsedResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_master_resume(
    file: UploadFile = File(...),
    replace: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload master resume PDF, parse text with PyMuPDF, segment sections, extract structured data and skills."""
    resume = await profile_service.process_master_resume_upload(
        db=db, user_id=current_user.id, file=file, replace=replace
    )
    
    sections = pdf_service.segment_sections(resume.raw_text)
    skills = pdf_service.detect_skills_deterministically(resume.raw_text)
    profile = profile_service.get_or_create_profile(db, current_user.id)
    comparison = profile_service.compare_extracted_data_with_profile(
        profile, resume.extracted_data or {}
    )

    return {
        "resume_id": resume.id,
        "filename": resume.filename,
        "file_size": resume.file_size,
        "raw_text": resume.raw_text,
        "sections": sections,
        "extracted_skills": skills,
        "extracted_data": resume.extracted_data,
        "comparison": comparison,
        "message": f"Successfully parsed {resume.filename} ({len(skills)} skills detected)",
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
