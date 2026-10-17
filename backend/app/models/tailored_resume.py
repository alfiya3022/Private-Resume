from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    version_number = Column(Integer, nullable=False, default=1)
    parent_version_id = Column(Integer, ForeignKey("tailored_resumes.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="draft", nullable=False)  # "draft" | "final"
    target_role = Column(String(150), nullable=True)

    # Content structure:
    # {
    #   "summary": "...",
    #   "skills": { "languages": [], "frameworks": [], "databases": [], "tools": [], "cloud": [] } or list,
    #   "experience": [ { "company": "", "title": "", "location": "", "start_date": "", "end_date": "", "bullets": [] } ],
    #   "projects": [ { "name": "", "technologies": [], "description": "", "bullets": [], "link": "" } ],
    #   "education": [ { "institution": "", "degree": "", "year": "", "gpa": "" } ],
    #   "certifications": [ { "name": "", "issuer": "", "year": "" } ]
    # }
    content = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
