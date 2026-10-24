import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.artifact import ResumeArtifact
from app.models.tailored_resume import TailoredResume
from app.schemas.tailored_resume import (
    TailoredResumeResponse,
    TailoredResumeUpdate,
    AskAIRequest,
    AskAIResponse,
)
from app.schemas.artifact import GeneratePdfResponse, ResumeArtifactResponse
from app.schemas.validation import ResumeValidationResponse
from app.services.tailoring_service import tailoring_service
from app.services.latex_service import latex_service
from app.services.validation_service import validation_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{resume_id}", response_model=TailoredResumeResponse)
def get_tailored_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a specific tailored resume version."""
    return tailoring_service.get_resume_or_404(db, current_user, resume_id)


@router.put("/{resume_id}", response_model=TailoredResumeResponse)
def update_tailored_resume(
    resume_id: int,
    update_data: TailoredResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update resume content or branch into a new version while preserving immutability."""
    return tailoring_service.update_resume(db, current_user, resume_id, update_data)


@router.post("/{resume_id}/edit", response_model=AskAIResponse)
async def ask_ai_edit_section(
    resume_id: int,
    request: AskAIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request localized AI revision for a specific resume section grounded in verified candidate evidence."""
    return await tailoring_service.ask_ai_edit(db, current_user, resume_id, request)


@router.post("/{resume_id}/finalize", response_model=TailoredResumeResponse)
def finalize_tailored_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lock tailored resume version as final/approved."""
    return tailoring_service.finalize_resume(db, current_user, resume_id)


@router.post("/{resume_id}/generate-pdf", response_model=GeneratePdfResponse)
def generate_pdf(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compile tailored resume into ATS-ready PDF via local LaTeX engine."""
    return latex_service.generate_resume_artifacts(db, current_user, resume_id)


@router.get("/{resume_id}/artifacts", response_model=List[ResumeArtifactResponse])
def get_resume_artifacts(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List compiled PDF and LaTeX source artifacts for target resume version."""
    tailoring_service.get_resume_or_404(db, current_user, resume_id)
    return (
        db.query(ResumeArtifact)
        .filter(ResumeArtifact.tailored_resume_id == resume_id, ResumeArtifact.user_id == current_user.id)
        .all()
    )


@router.get("/{resume_id}/pdf")
def preview_or_download_pdf(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream generated PDF for inline browser preview or direct download."""
    tailoring_service.get_resume_or_404(db, current_user, resume_id)
    artifact = (
        db.query(ResumeArtifact)
        .filter(
            ResumeArtifact.tailored_resume_id == resume_id,
            ResumeArtifact.user_id == current_user.id,
            ResumeArtifact.artifact_type == "pdf",
        )
        .first()
    )
    if not artifact or not Path(artifact.file_path).exists():
        # Automatically compile on-the-fly if not already generated
        try:
            latex_service.generate_resume_artifacts(db, current_user, resume_id)
            artifact = (
                db.query(ResumeArtifact)
                .filter(
                    ResumeArtifact.tailored_resume_id == resume_id,
                    ResumeArtifact.user_id == current_user.id,
                    ResumeArtifact.artifact_type == "pdf",
                )
                .first()
            )
        except Exception as e:
            logger.error(
                "Failed to compile PDF for tailored resume %s: %s",
                resume_id,
                e,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to compile resume PDF.",
            )

    if not artifact or not Path(artifact.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found. Please compile the resume first.",
        )
    return FileResponse(
        path=artifact.file_path,
        media_type="application/pdf",
        filename=Path(artifact.file_path).name,
        content_disposition_type="inline",
    )


@router.get("/{resume_id}/tex")
def download_tex_source(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream generated LaTeX source code file."""
    tailoring_service.get_resume_or_404(db, current_user, resume_id)
    artifact = (
        db.query(ResumeArtifact)
        .filter(
            ResumeArtifact.tailored_resume_id == resume_id,
            ResumeArtifact.user_id == current_user.id,
            ResumeArtifact.artifact_type == "tex",
        )
        .first()
    )
    if not artifact or not Path(artifact.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LaTeX source file not found.",
        )
    return FileResponse(
        path=artifact.file_path,
        media_type="text/plain",
        filename=Path(artifact.file_path).name,
    )


@router.post("/{resume_id}/validate", response_model=ResumeValidationResponse)
def validate_tailored_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run automated multi-point ATS pre-flight validation on the compiled PDF."""
    return validation_service.validate_resume(db, current_user, resume_id)


@router.get("/{resume_id}/validation", response_model=ResumeValidationResponse)
def get_resume_validation(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve existing validation diagnostics for target resume version."""
    return validation_service.get_validation(db, current_user, resume_id)
