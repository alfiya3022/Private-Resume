from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class ResumeExperienceItem(BaseModel):
    company: str = ""
    title: str = ""
    location: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    bullets: List[str] = Field(default_factory=list)


class ResumeProjectItem(BaseModel):
    name: str = ""
    technologies: List[str] = Field(default_factory=list)
    description: Optional[str] = ""
    bullets: List[str] = Field(default_factory=list)
    link: Optional[str] = ""


class ResumeEducationItem(BaseModel):
    institution: str = ""
    degree: str = ""
    year: Optional[str] = ""
    gpa: Optional[str] = ""


class ResumeCertificationItem(BaseModel):
    name: str = ""
    issuer: Optional[str] = ""
    year: Optional[str] = ""


class TailoredResumeContent(BaseModel):
    summary: str = ""
    skills: Dict[str, List[str]] = Field(default_factory=dict)
    experience: List[ResumeExperienceItem] = Field(default_factory=list)
    projects: List[ResumeProjectItem] = Field(default_factory=list)
    education: List[ResumeEducationItem] = Field(default_factory=list)
    certifications: List[ResumeCertificationItem] = Field(default_factory=list)


class TailoredResumeUpdate(BaseModel):
    content: Dict[str, Any]
    target_role: Optional[str] = None
    save_as_new_version: bool = True


class AskAIRequest(BaseModel):
    section: str = Field(..., description="Section being refined (e.g. 'summary', 'experience', 'projects')")
    instruction: str = Field(..., description="Prompt or instruction for revision")
    current_text: Optional[str] = Field(None, description="Current content of the section or bullet")


class AskAIResponse(BaseModel):
    section: str
    suggested_text: str
    explanation: str
    factuality_checked: bool = True


class TailoredResumeResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    version_number: int
    parent_version_id: Optional[int] = None
    status: str
    target_role: Optional[str] = None
    content: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
