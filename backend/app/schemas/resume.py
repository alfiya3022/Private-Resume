from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class MasterResumeResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_size: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParsedResumeSection(BaseModel):
    name: str
    content: str
    items: List[str] = []


class ParsedResumeResponse(BaseModel):
    resume_id: int
    filename: str
    file_size: int
    raw_text: str
    sections: Dict[str, str] = {}
    extracted_skills: List[str] = []
    message: str = "Master resume parsed successfully"
