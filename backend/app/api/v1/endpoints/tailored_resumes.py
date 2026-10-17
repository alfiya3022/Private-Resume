from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.tailored_resume import (
    TailoredResumeResponse,
    TailoredResumeUpdate,
    AskAIRequest,
    AskAIResponse,
)
from app.services.tailoring_service import tailoring_service

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
