from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ResumeArtifactResponse(BaseModel):
    id: int
    tailored_resume_id: int
    user_id: int
    artifact_type: str
    file_path: str
    file_size: Optional[int] = None
    compilation_log: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GeneratePdfResponse(BaseModel):
    pdf_artifact_id: int
    tex_artifact_id: int
    pdf_download_url: str
    tex_download_url: str
    success: bool
    compilation_log: Optional[str] = None
