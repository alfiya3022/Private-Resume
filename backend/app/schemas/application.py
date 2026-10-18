from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ApplicationCreate(BaseModel):
    job_id: int
    tailored_resume_id: Optional[int] = None
    status: Optional[str] = Field("applied", pattern="^(draft|applied|interviewing|offer|rejected|archived)$")
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(draft|applied|interviewing|offer|rejected|archived)$")
    notes: Optional[str] = None


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    title: str
    location: Optional[str] = None
    status: str


class TailoredResumeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: int
    status: str
    target_role: Optional[str] = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    job_id: int
    tailored_resume_id: Optional[int] = None
    status: str
    applied_date: datetime
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Associated summaries
    job: Optional[JobSummary] = None
    tailored_resume: Optional[TailoredResumeSummary] = None
