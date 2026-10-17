from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class SkillEvidenceItem(BaseModel):
    skill: str
    status: str  # "matched", "weak", "missing", "unsupported"
    evidence_sources: List[str] = []
    explanation: str


class MatchAnalysisResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    estimated_match_score: int
    matched_skills: List[str] = []
    weak_skills: List[str] = []
    missing_skills: List[str] = []
    unsupported_claims: List[str] = []
    evidence_map: Dict[str, List[str]] = {}
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
