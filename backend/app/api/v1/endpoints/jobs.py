from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.schemas.analysis import JobAnalysisResponse
from app.schemas.match import MatchAnalysisResponse
from app.services.job_service import job_service



router = APIRouter()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create and persist a new target job opportunity and raw job description."""
    return job_service.create_job(db=db, user_id=current_user.id, job_in=job_in)


@router.get("", response_model=List[JobResponse])
def list_jobs(
    status: Optional[str] = Query(None, description="Filter by job status (active, archived)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all saved jobs for the authenticated candidate."""
    return job_service.list_jobs(db=db, user_id=current_user.id, status_filter=status)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a specific job record by ID."""
    job = job_service.get_job(db=db, user_id=current_user.id, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update job metadata or raw job description content."""
    job = job_service.update_job(
        db=db, user_id=current_user.id, job_id=job_id, job_in=job_in
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a target job record."""
    success = job_service.delete_job(
        db=db, user_id=current_user.id, job_id=job_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )


@router.post("/{job_id}/analyze", response_model=JobAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger AI/deterministic analysis of the target job description."""
    from app.services.analysis_service import analysis_service
    return await analysis_service.analyze_job(db=db, user_id=current_user.id, job_id=job_id)


@router.get("/{job_id}/analysis", response_model=JobAnalysisResponse)
def get_job_analysis(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve previously generated structured requirements for this job."""
    from app.services.analysis_service import analysis_service
    analysis = analysis_service.get_analysis_by_job_id(db=db, user_id=current_user.id, job_id=job_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found for this job. Trigger analysis first.",
        )
    return analysis


@router.post("/{job_id}/match", response_model=MatchAnalysisResponse, status_code=status.HTTP_200_OK)
def match_resume_to_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run deterministic matching between candidate profile and target job requirements."""
    from app.services.matching_service import matching_service
    return matching_service.calculate_match(db=db, user_id=current_user.id, job_id=job_id)


@router.get("/{job_id}/match", response_model=MatchAnalysisResponse)
def get_job_match(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve existing match analysis for target job."""
    from app.services.matching_service import matching_service
    match_data = matching_service.get_match_by_job_id(db=db, user_id=current_user.id, job_id=job_id)
    if not match_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match analysis not found for this job. Trigger matching first.",
        )
    return match_data


