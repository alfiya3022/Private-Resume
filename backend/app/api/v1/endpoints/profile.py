from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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
    ProjectUpdate,
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
    EducationCreate,
    EducationResponse,
    EducationUpdate,
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
    GitHubExtractRequest,
    GitHubExtractResponse,
)
from app.services.profile_service import profile_service
from app.services.github_service import github_service
from app.services.latex_service import latex_service

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


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a project in candidate profile."""
    updated = profile_service.update_project(db, current_user.id, project_id, project_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return updated


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


@router.put("/experiences/{exp_id}", response_model=ExperienceResponse)
def update_experience(
    exp_id: int,
    exp_in: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update work experience entry in candidate profile."""
    updated = profile_service.update_experience(db, current_user.id, exp_id, exp_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found"
        )
    return updated


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


@router.put("/educations/{edu_id}", response_model=EducationResponse)
def update_education(
    edu_id: int,
    edu_in: EducationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update education record in candidate profile."""
    updated = profile_service.update_education(db, current_user.id, edu_id, edu_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found"
        )
    return updated


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


@router.put("/certifications/{cert_id}", response_model=CertificationResponse)
def update_certification(
    cert_id: int,
    cert_in: CertificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update certification record in candidate profile."""
    updated = profile_service.update_certification(db, current_user.id, cert_id, cert_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found"
        )
    return updated


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


# Section Reset and Global Reset Endpoints
@router.delete("/sections/{section}", response_model=ProfileResponse)
def reset_profile_section(
    section: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all persisted records in a specific profile section for the authenticated user."""
    return profile_service.reset_section(db, current_user.id, section)


@router.delete("/reset-all", response_model=ProfileResponse)
def reset_all_profile_sections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all persisted records across all six profile sections for the authenticated user."""
    return profile_service.reset_all(db, current_user.id)


@router.delete("/personal", response_model=ProfileResponse)
def reset_personal_section(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Clear all personal metadata fields for the authenticated user."""
    return profile_service.reset_section(db, current_user.id, "personal")


@router.delete("/skills", response_model=ProfileResponse)
def reset_skills_section(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all verified candidate skills for the authenticated user."""
    return profile_service.reset_section(db, current_user.id, "skills")


@router.delete("/projects", response_model=ProfileResponse)
def reset_projects_section(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all projects for the authenticated user."""
    return profile_service.reset_section(db, current_user.id, "projects")


@router.delete("/experiences", response_model=ProfileResponse)
def reset_experiences_section(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all experience records for the authenticated user."""
    return profile_service.reset_section(db, current_user.id, "experiences")


@router.delete("/educations", response_model=ProfileResponse)
def reset_educations_section(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all education records for the authenticated user."""
    return profile_service.reset_section(db, current_user.id, "educations")


@router.delete("/certifications", response_model=ProfileResponse)
def reset_certifications_section(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all certification records for the authenticated user."""
    return profile_service.reset_section(db, current_user.id, "certifications")


@router.delete("", response_model=ProfileResponse)
def delete_entire_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reset all profile sections for the authenticated user."""
    return profile_service.reset_all(db, current_user.id)


# Custom LaTeX Template Endpoints
MAX_TEMPLATE_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/template")
async def upload_custom_template(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Uploads a custom LaTeX template (.tex or .zip package) for candidate PDF compilation."""
    try:
        # Read at most one byte beyond the limit so oversized uploads are rejected
        # without loading the complete file into memory.
        content = await file.read(MAX_TEMPLATE_UPLOAD_BYTES + 1)
    finally:
        await file.close()

    if len(content) > MAX_TEMPLATE_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Template uploads must be 10 MB or smaller.",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    result = latex_service.save_user_template(current_user.id, file.filename, content)
    latex_service.invalidate_user_artifacts(db, current_user.id)
    return result


@router.get("/template")
def get_custom_template(
    current_user: User = Depends(get_current_user),
):
    """Retrieves metadata of the candidate's active custom LaTeX template."""
    return latex_service.get_user_template_info(current_user.id)


@router.delete("/template")
def delete_custom_template(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes custom template and reverts to system default Modern Editorial."""
    latex_service.delete_user_template(current_user.id)
    latex_service.invalidate_user_artifacts(db, current_user.id)
    return {"status": "success", "message": "Reverted to default LaTeX template."}
