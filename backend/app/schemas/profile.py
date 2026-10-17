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


class ExperienceBase(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    bullets: List[str] = []
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    id: int
    profile_id: int

    model_config = ConfigDict(from_attributes=True)


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


class CertificationBase(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationResponse(CertificationBase):
    id: int
    profile_id: int

    model_config = ConfigDict(from_attributes=True)


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
