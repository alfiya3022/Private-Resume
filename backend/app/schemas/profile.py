from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SkillBase(BaseModel):
    name: str
    category: Optional[str] = "General"
    proficiency: Optional[str] = "Intermediate"


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: int
    profile_id: int

    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    title: str
    role: Optional[str] = None
    description: Optional[str] = None
    bullets: List[str] = []
    technologies: List[str] = []
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    profile_id: int

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    bullets: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExperienceBase(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    bullets: List[str] = []
    technologies: List[str] = []
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    id: int
    profile_id: int

    model_config = ConfigDict(from_attributes=True)


class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    bullets: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None


class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    grade: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: int
    profile_id: int

    model_config = ConfigDict(from_attributes=True)


class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    grade: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CertificationBase(BaseModel):
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    item_type: Optional[str] = "certification"
    status_note: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationResponse(CertificationBase):
    id: int
    profile_id: int

    model_config = ConfigDict(from_attributes=True)


class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    item_type: Optional[str] = None
    status_note: Optional[str] = None
    credential_url: Optional[str] = None


class ProfileUpdate(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    headline: Optional[str] = None
    summary: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    skills: List[SkillResponse] = []
    projects: List[ProjectResponse] = []
    experiences: List[ExperienceResponse] = []
    educations: List[EducationResponse] = []
    certifications: List[CertificationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class GitHubExtractRequest(BaseModel):
    github_url: str


class GitHubExtractResponse(BaseModel):
    title: str
    role: Optional[str] = "Creator / Maintainer"
    description: Optional[str] = None
    technologies: List[str] = []
    bullets: List[str] = []
    url: str
