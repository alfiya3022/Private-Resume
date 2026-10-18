from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime


class ValidationCheckItem(BaseModel):
    name: str
    status: str  # "PASS", "WARN", "FAIL"
    title: str
    message: str
    details: Optional[Any] = None


class ResumeValidationResponse(BaseModel):
    id: int
    tailored_resume_id: int
    user_id: int
    overall_status: str  # "PASS", "WARN", "FAIL"
    score: int
    checks: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
