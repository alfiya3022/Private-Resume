from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class ResumeArtifact(Base):
    __tablename__ = "resume_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    tailored_resume_id = Column(
        Integer, ForeignKey("tailored_resumes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    artifact_type = Column(String(50), nullable=False)  # "pdf" | "tex"
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    compilation_log = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
