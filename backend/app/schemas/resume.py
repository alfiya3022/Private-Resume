from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict


class MasterResumeResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_size: int
    is_active: bool
    parse_status: str = "complete"
    parse_stage: Optional[str] = None
    parse_error: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParsedResumeSection(BaseModel):
    name: str
    content: str
    items: List[str] = []


class ResumeUploadQueuedResponse(BaseModel):
    resume_id: int
    filename: str
    parse_status: str = "queued"
    message: str = "Resume upload accepted and queued for background extraction"


class ResumeStatusResponse(BaseModel):
    resume_id: int
    parse_status: str  # queued, running, complete, failed
    parse_stage: Optional[str] = None
    parse_error: Optional[str] = None


class ParsedResumeResponse(BaseModel):
    resume_id: int
    filename: str
    file_size: int
    raw_text: str
    sections: Dict[str, str] = {}
    extracted_skills: List[str] = []
    extracted_data: Optional[Dict[str, Any]] = None
    comparison: Optional[Dict[str, Any]] = None
    parse_status: Optional[str] = "complete"
    message: str = "Master resume parsed successfully"


class ApplyExtractedDataRequest(BaseModel):
    sections: Optional[List[str]] = None
    overwrite_existing: bool = False
    edited_data: Optional[Dict[str, Any]] = None
    item_decisions: Optional[Dict[str, str]] = None
    remember_corrections: Optional[List[Dict[str, Any]]] = None


class ExtractedDataComparisonResponse(BaseModel):
    resume_id: int
    filename: str
    extracted_data: Dict[str, Any] = {}
    comparison: Dict[str, Any] = {}
    is_active: bool = True
