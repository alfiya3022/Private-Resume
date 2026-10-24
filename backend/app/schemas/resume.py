from datetime import datetime
from typing import Dict, List, Optional, Any
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
    extracted_data: Optional[Dict[str, Any]] = None
    comparison: Optional[Dict[str, Any]] = None
    message: str = "Master resume parsed successfully"


class ApplyExtractedDataRequest(BaseModel):
    sections: Optional[List[str]] = None
    overwrite_existing: bool = False


class ExtractedDataComparisonResponse(BaseModel):
    resume_id: int
    filename: str
    extracted_data: Dict[str, Any] = {}
    comparison: Dict[str, Any] = {}
    is_active: bool = True
