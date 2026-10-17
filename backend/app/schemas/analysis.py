from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


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
    soft_skills: List[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
