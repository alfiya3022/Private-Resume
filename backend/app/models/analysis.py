from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)

    required_skills = Column(JSON, default=list, nullable=False)
    preferred_skills = Column(JSON, default=list, nullable=False)
    languages = Column(JSON, default=list, nullable=False)
    frameworks = Column(JSON, default=list, nullable=False)
    databases = Column(JSON, default=list, nullable=False)
    tools = Column(JSON, default=list, nullable=False)
    cloud = Column(JSON, default=list, nullable=False)
    responsibilities = Column(JSON, default=list, nullable=False)
    qualifications = Column(JSON, default=list, nullable=False)
    experience_years = Column(String(100), nullable=True)
    soft_skills = Column(JSON, default=list, nullable=False)
    raw_analysis = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
