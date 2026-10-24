from typing import List, Optional
from pydantic import BaseModel, Field


class LLMPersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class LLMEducationItem(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    grade: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class LLMExperienceItem(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class LLMProjectItem(BaseModel):
    title: str
    role: Optional[str] = None
    description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class LLMCertificationItem(BaseModel):
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None


class LLMResumeExtraction(BaseModel):
    personal_info: Optional[LLMPersonalInfo] = None
    summary: Optional[str] = None
    education: List[LLMEducationItem] = Field(default_factory=list)
    experience: List[LLMExperienceItem] = Field(default_factory=list)
    projects: List[LLMProjectItem] = Field(default_factory=list)
    certifications: List[LLMCertificationItem] = Field(default_factory=list)


class LLMChunkSkills(BaseModel):
    skills: List[str] = Field(default_factory=list)


class LLMSkillCategoryItem(BaseModel):
    skill: str
    category: str


class LLMSkillCategoryBatch(BaseModel):
    items: List[LLMSkillCategoryItem] = Field(default_factory=list)
