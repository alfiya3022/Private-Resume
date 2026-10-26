import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import UploadFile

from app.core.database import Base
from app.models.user import User
from app.models.profile import CandidateProfile, CandidateSkill, CareerKnowledgeItem
from app.services.career_knowledge_service import (
    career_knowledge_service,
    normalize_term,
    compute_deterministic_vector,
    cosine_similarity,
)
from app.services.pdf_service import pdf_service
from app.services.skill_pipeline import skill_pipeline, appears_in_source, find_source_evidence
from app.core.diagnostics import ProcessingDiagnostics


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = TestingSession()
    
    # Create test user
    user = User(
        id=101,
        email="candidate@Verity.local",
        hashed_password="hashed_pw_secret",
        full_name="Jane Doe",
        is_active=True,
    )
    session.add(user)
    session.commit()
    
    yield session
    session.close()


def test_pdf_segment_sections_preserves_custom_headings():
    """Verifies that unknown or unfamiliar section headings are preserved as distinct

    sections rather than silently dropped.
    """
    resume_text = """
Jane Doe
jane@example.com

PROFESSIONAL JOURNEY
Staff Engineer leading distributed backend systems for 5 years.

CAREER HIGHLIGHTS
- Spearheaded zero-downtime database migration for 10M records
- Architected event-driven microservices

SKILLS
Python, PostgreSQL, FastAPI, Docker

TECHNICAL CONTRIBUTIONS
Authored internal open-source library for resilient API retries.
"""
    sections = pdf_service.segment_sections(resume_text)
    
    # Standard sections detected
    assert "skills" in sections
    assert "Python, PostgreSQL" in sections["skills"]

    # Unknown custom sections preserved
    assert "PROFESSIONAL JOURNEY" in sections
    assert "Staff Engineer" in sections["PROFESSIONAL JOURNEY"]
    
    assert "CAREER HIGHLIGHTS" in sections
    assert "zero-downtime" in sections["CAREER HIGHLIGHTS"]

    assert "TECHNICAL CONTRIBUTIONS" in sections
    assert "open-source" in sections["TECHNICAL CONTRIBUTIONS"]


def test_appears_in_source_with_aliases_and_evidence():
    """Tests that appears_in_source recognizes standard aliases (Postgres vs PostgreSQL,

    React vs React.js) and extracts exact source evidence.
    """
    source_text = """
Experience:
Senior Software Engineer at Acme Corp (2021 - Present)
- Developed RESTful APIs using Python, Postgres and React
- Deployed scalable worker containers with K8s and AWS
- Engineered reliable caching using Redis
"""
    # Direct substring
    assert appears_in_source("Python", source_text) is True
    assert appears_in_source("Redis", source_text) is True

    # Known aliases should resolve
    assert appears_in_source("PostgreSQL", source_text) is True  # source has 'Postgres'
    assert appears_in_source("React.js", source_text) is True    # source has 'React'
    assert appears_in_source("Kubernetes", source_text) is True  # source has 'K8s'
    assert appears_in_source("Amazon Web Services", source_text) is True  # source has 'AWS'

    # Hallucinated skills must not pass
    assert appears_in_source("Java Spring Boot", source_text) is False
    assert appears_in_source("Ruby on Rails", source_text) is False

    # Evidence extraction
    evidence = find_source_evidence("Postgres", source_text)
    assert evidence is not None
    assert "Developed RESTful APIs using Python, Postgres and React" in evidence


def test_unknown_skill_preservation():
    """Verifies that unfamiliar, domain-specific, or non-technical skills

    present in the resume text are preserved and categorized as 'Other' or domain category.
    """
    text = "Core Competencies: Regulatory Auditing, Six Sigma Green Belt, Talent Sourcing, Tally ERP"
    assert appears_in_source("Regulatory Auditing", text) is True
    assert appears_in_source("Six Sigma Green Belt", text) is True
    assert appears_in_source("Tally ERP", text) is True


def test_career_knowledge_isolation_between_resume_and_jd(in_memory_db):
    """Ensures that skills mentioned in a job description are strictly isolated

    and NEVER leak into candidate demonstrated skills.
    """
    db = in_memory_db
    user_id = 101

    # 1. Candidate demonstrates Python & FastAPI in master resume
    career_knowledge_service.record_knowledge_item(
        db=db,
        user_id=user_id,
        knowledge_type="skill",
        source_type="master_resume",
        source_id="resume-1",
        original_text="Python",
        category="Programming Language",
        source_evidence="5 years Python backend development",
        review_status="extracted",
    )
    career_knowledge_service.record_knowledge_item(
        db=db,
        user_id=user_id,
        knowledge_type="skill",
        source_type="master_resume",
        source_id="resume-1",
        original_text="FastAPI",
        category="Backend Framework",
        source_evidence="Built async REST APIs with FastAPI",
        review_status="confirmed",
    )

    # 2. A job description requires Golang & Rust
    career_knowledge_service.record_knowledge_item(
        db=db,
        user_id=user_id,
        knowledge_type="skill",
        source_type="job_description",
        source_id="jd-99",
        original_text="Golang",
        category="Programming Language",
        source_evidence="Must have 3+ years in Golang",
        review_status="extracted",
    )
    career_knowledge_service.record_knowledge_item(
        db=db,
        user_id=user_id,
        knowledge_type="skill",
        source_type="job_description",
        source_id="jd-99",
        original_text="Rust",
        category="Programming Language",
        source_evidence="Nice to have Rust experience",
        review_status="extracted",
    )

    # 3. Retrieve demonstrated skills
    demonstrated = career_knowledge_service.get_candidate_demonstrated_skills(db, user_id)
    demonstrated_names = {item.normalized_term for item in demonstrated}

    # Candidate skills MUST be present
    assert "Python" in demonstrated_names
    assert "FastAPI" in demonstrated_names

    # Job description requirements MUST NOT be in candidate demonstrated skills
    assert "Golang" not in demonstrated_names
    assert "Go" not in demonstrated_names
    assert "Rust" not in demonstrated_names


def test_semantic_relationship_classification():
    """Verifies semantic relationship distinctions: Exact match, Known alias,

    Broader/narrower concept, Semantically related concept, Uncertain relationship.
    """
    # 1. Exact match
    res1 = career_knowledge_service.classify_relationship("PostgreSQL", "PostgreSQL")
    assert res1["relationship"] == "Exact match"
    assert res1["is_match"] is True

    # 2. Known alias
    res2 = career_knowledge_service.classify_relationship("postgres", "postgresql")
    assert res2["relationship"] in ["Exact match", "Known alias"]
    assert res2["is_match"] is True

    res3 = career_knowledge_service.classify_relationship("react", "react.js")
    assert res3["is_match"] is True

    # 3. Broader or narrower concept
    res4 = career_knowledge_service.classify_relationship("SQL", "Complex SQL Queries")
    assert res4["relationship"] == "Broader or narrower concept"
    assert res4["is_match"] is True

    # 4. Uncertain / non-match
    res5 = career_knowledge_service.classify_relationship("Docker", "Accounting Ledger")
    assert res5["is_match"] is False


def test_user_correction_persistence(in_memory_db):
    """Verifies that user corrections are persisted with appropriate metadata."""
    db = in_memory_db
    user_id = 101

    item = career_knowledge_service.record_user_correction(
        db=db,
        user_id=user_id,
        field_name="skill",
        original_value="Pythn",
        corrected_value="Python",
        category="Programming Language",
        source_id="resume-1",
    )
    assert item.id is not None
    assert item.normalized_term == "Python"
    assert item.source_type == "user_correction"
    assert item.review_status == "confirmed"
    assert "User corrected" in item.source_evidence


def test_diagnostics_tracking():
    """Verifies diagnostic stage tracking, duration measurement, and summary reporting."""
    diag = ProcessingDiagnostics(correlation_id="test-corr-42")
    
    with diag.track_stage("pdf_validation", doc_type="pdf"):
        pass

    with diag.track_stage("text_extraction", pages=2):
        pass

    diag.log_ollama_call(
        operation="extract_skills",
        model="qwen3:4b-instruct",
        duration_ms=45.2,
        input_chars=1200,
        output_chars=180,
        success=True,
    )

    summary = diag.get_summary()
    assert summary["correlation_id"] == "test-corr-42"
    assert "pdf_validation" in summary["stages"]
    assert summary["stages"]["pdf_validation"]["status"] == "SUCCESS"
    assert summary["stages"]["text_extraction"]["pages"] == 2
    assert summary["error_count"] == 0
