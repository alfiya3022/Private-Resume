from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
    SkillCreate,
    SkillResponse,
    ProjectCreate,
    ProjectResponse,
    ExperienceCreate,
    ExperienceResponse,
    EducationCreate,
    EducationResponse,
    CertificationCreate,
    CertificationResponse,
    GitHubExtractRequest,
    GitHubExtractResponse,
)
from app.services.profile_service import profile_service
from app.services.github_service import github_service

router = APIRouter()


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the authenticated candidate's structured master profile."""
    return profile_service.get_or_create_profile(db, current_user.id)


@router.put("", response_model=ProfileResponse)
def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile metadata and overview information."""
    return profile_service.update_profile(db, current_user.id, profile_in)


# Skills
@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def add_skill(
    skill_in: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a verified candidate skill."""
    return profile_service.add_skill(db, current_user.id, skill_in)


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a skill from candidate profile."""
    success = profile_service.delete_skill(db, current_user.id, skill_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found"
        )


# Projects
@router.post("/projects/extract-github", response_model=GitHubExtractResponse)
async def extract_github_project(
    request: GitHubExtractRequest,
    current_user: User = Depends(get_current_user),
):
    """Extract project information, stack, and accomplishments from a GitHub repository."""
    if not request.github_url or not request.github_url.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub URL is required"
        )
    return await github_service.extract_project_from_github(request.github_url)


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def add_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a verified project with associated evidence."""
    return profile_service.add_project(db, current_user.id, project_in)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project from candidate profile."""
    success = profile_service.delete_project(db, current_user.id, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )


# Experiences
@router.post("/experiences", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
def add_experience(
    exp_in: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add work experience entry."""
    return profile_service.add_experience(db, current_user.id, exp_in)


@router.delete("/experiences/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete experience entry."""
    success = profile_service.delete_experience(db, current_user.id, exp_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found"
        )


# Educations
@router.post("/educations", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
def add_education(
    edu_in: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add education record."""
    return profile_service.add_education(db, current_user.id, edu_in)


@router.delete("/educations/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(
    edu_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete education record."""
    success = profile_service.delete_education(db, current_user.id, edu_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found"
        )


# Certifications
@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
def add_certification(
    cert_in: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add certification record."""
    return profile_service.add_certification(db, current_user.id, cert_in)


@router.delete("/certifications/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(
    cert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete certification record."""
    success = profile_service.delete_certification(db, current_user.id, cert_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found"
        )
