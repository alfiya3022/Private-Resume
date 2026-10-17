from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class JobBase(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    job_url: Optional[str] = None
    salary: Optional[str] = None
    raw_jd_text: str

    @field_validator("company", "title", "raw_jd_text")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or blank")
        return v.strip()


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None
    salary: Optional[str] = None
    raw_jd_text: Optional[str] = None
    status: Optional[str] = None


class JobResponse(JobBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
