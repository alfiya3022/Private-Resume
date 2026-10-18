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
    download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GeneratePdfResponse(BaseModel):
    status: str
    message: str
    pdf_artifact: ResumeArtifactResponse
    tex_artifact: Optional[ResumeArtifactResponse] = None
