from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    headline = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    skills = relationship("CandidateSkill", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="profile", cascade="all, delete-orphan")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), index=True, nullable=False)
    category = Column(String(100), nullable=True)  # Language, Framework, Database, Tool, etc.
    proficiency = Column(String(50), nullable=True)  # Beginner, Intermediate, Advanced

    profile = relationship("CandidateProfile", back_populates="skills")
    source_evidence = Column(Text, nullable=True)
    review_status = Column(String(50), default="confirmed", nullable=True)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    role = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    bullets = Column(JSON, default=list, nullable=False)  # List of accomplishment bullet strings
    technologies = Column(JSON, default=list, nullable=False)  # Associated tech stack
    url = Column(String(255), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)

    profile = relationship("CandidateProfile", back_populates="projects")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    company = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    bullets = Column(JSON, default=list, nullable=False)
    technologies = Column(JSON, default=list, nullable=False)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False, nullable=False)

    profile = relationship("CandidateProfile", back_populates="experiences")


class Education(Base):
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    grade = Column(String(50), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)

    profile = relationship("CandidateProfile", back_populates="educations")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    item_type = Column(String(50), default="certification", nullable=False)
    status_note = Column(String(100), nullable=True)
    credential_url = Column(String(255), nullable=True)

    profile = relationship("CandidateProfile", back_populates="certifications")


class CareerKnowledgeItem(Base):
    __tablename__ = "career_knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    knowledge_type = Column(String(50), nullable=False, default="skill")  # skill, experience, project, certification, domain
    source_type = Column(String(50), nullable=False)  # master_resume, job_description, user_correction, user_profile
    source_id = Column(String(100), nullable=True)  # resume_id or job_id
    original_text = Column(String(255), nullable=False)
    normalized_term = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    aliases = Column(JSON, default=list, nullable=False)
    source_evidence = Column(Text, nullable=True)
    source_page = Column(Integer, nullable=True)
    review_status = Column(String(50), default="extracted", nullable=False)  # extracted, confirmed, rejected, user_added
    confidence_score = Column(Integer, default=100, nullable=False)
    embedding = Column(JSON, nullable=True)  # 384-dimensional embedding vector stored as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", backref="career_knowledge_items")

