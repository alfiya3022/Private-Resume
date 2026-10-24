from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, model_validator


class StructuredJDAnalysis(BaseModel):
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    languages: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    tools: List[str] = []
    cloud: List[str] = []
    responsibilities: List[str] = []
    qualifications: List[str] = []
    experience_years: Optional[str] = None
    min_years: Optional[int] = None
    max_years: Optional[int] = None
    experience_range: Optional[str] = None
    soft_skills: List[str] = []


class JobAnalysisResponse(BaseModel):
    id: int
    job_id: int
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    languages: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    tools: List[str] = []
    cloud: List[str] = []
    responsibilities: List[str] = []
    qualifications: List[str] = []
    experience_years: Optional[str] = None
    min_years: Optional[int] = None
    max_years: Optional[int] = None
    experience_range: Optional[str] = None
    soft_skills: List[str] = []
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def populate_display_experience(self) -> "JobAnalysisResponse":
        if self.experience_range and self.experience_range != "Not specified":
            self.experience_years = self.experience_range
        return self

    model_config = ConfigDict(from_attributes=True)
