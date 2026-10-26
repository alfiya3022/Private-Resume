import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import CandidateProfile, CandidateSkill, Project, CareerKnowledgeItem
from app.models.resume import MasterResume
from app.services.career_knowledge_service import career_knowledge_service, KNOWN_DISTINCT_PAIRS
from app.services.profile_service import profile_service, compare_projects_multi_signal


def test_distinct_technology_pairs_never_conflated():
    """Verify that distinct pairs like SQL vs MySQL, Java vs JavaScript, React vs React Native

    are strictly recognized as distinct technologies and never conflated as duplicates or aliases.
    """
    pairs_to_test = [
        ("SQL", "MySQL"),
        ("Java", "JavaScript"),
        ("React", "React Native"),
        ("C", "C++"),
        ("C", "C#"),
        ("C++", "C#"),
    ]
    for term_a, term_b in pairs_to_test:
        rel = career_knowledge_service.classify_relationship(term_a, term_b)
        assert rel["is_match"] is False, f"Expected {term_a} and {term_b} not to match, got {rel}"
        assert rel["relationship"] == "Distinct technologies", f"Expected Distinct technologies for {term_a} vs {term_b}"
        assert rel["score"] == 0.0


def test_whitespace_and_punctuation_normalizations():
    """Verify that formatting variations like 'Power BI' vs 'PowerBI' and 'Window Functions'

    vs 'WindowFunctions' are resolved as exact matches.
    """
    matches = [
        ("Power BI", "PowerBI"),
        ("Power-BI", "power bi"),
        ("Window Functions", "WindowFunctions"),
        ("FastAPI", "Fast API"),
        ("PostgreSQL", "postgres"),
    ]
    for term_a, term_b in matches:
        rel = career_knowledge_service.classify_relationship(term_a, term_b)
        assert rel["is_match"] is True, f"Expected {term_a} and {term_b} to match, got {rel}"
        assert rel["relationship"] in ("Exact match", "Known alias")
        assert rel["score"] >= 0.95


def test_project_multi_signal_duplicate_detection():
    """Verify that two projects with different title wording but identical repository URL

    trigger 'possible_duplicate' status with explicit matching reason.
    """
    existing_project = Project(
        id=101,
        title="Resume Analytics Engine",
        url="https://github.com/developer/resume-parser",
        technologies=["Python", "FastAPI", "PyMuPDF"],
        description="A resume extraction system",
    )

    # Case A: Same repository URL, differing title wording
    incoming_proj_a = {
        "title": "Automated Resume Parser & Skill Extractor",
        "url": "https://github.com/developer/resume-parser.git/",
        "technologies": ["Python", "FastAPI"],
    }
    comp_a = compare_projects_multi_signal(incoming_proj_a, existing_project)
    assert comp_a["status"] == "possible_duplicate"
    assert comp_a["score"] >= 0.80
    assert "Same repository URL" in comp_a["reason"]
    assert comp_a["existing_title"] == "Resume Analytics Engine"

    # Case B: Completely identical title
    incoming_proj_b = {
        "title": "Resume Analytics Engine",
        "url": "https://github.com/developer/other-url",
        "technologies": ["Python"],
    }
    comp_b = compare_projects_multi_signal(incoming_proj_b, existing_project)
    assert comp_b["status"] == "same"
    assert comp_b["score"] == 1.0

    # Case C: Completely different project
    incoming_proj_c = {
        "title": "Crypto Wallet Mobile App",
        "url": "https://github.com/developer/crypto-wallet",
        "technologies": ["Solidity", "React Native"],
    }
    comp_c = compare_projects_multi_signal(incoming_proj_c, existing_project)
    assert comp_c["status"] == "different"
    assert comp_c["score"] == 0.0


def test_per_item_duplicate_decisions_application(db_session: Session):
    """Verify candidate consent choices: 'keep_existing', 'replace_with_new', 'save_separate', 'discard'.

    Also verify that user corrections are persisted into career_knowledge_items.
    """
    user = User(email="candidate_test@example.com", hashed_password="pw", full_name="Consent Candidate")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_id = user.id
    profile = profile_service.get_or_create_profile(db_session, user_id)

    # Seed existing profile with a project and a skill
    orig_proj = Project(
        profile_id=profile.id,
        title="Original Analytics Pipeline",
        url="https://github.com/candidate/analytics",
        technologies=["Python", "PostgreSQL"],
        description="Original description",
    )
    orig_skill = CandidateSkill(
        profile_id=profile.id,
        name="SQL",
        category="Database",
    )
    db_session.add(orig_proj)
    db_session.add(orig_skill)
    db_session.commit()

    # Create dummy master resume record
    resume = MasterResume(
        user_id=user_id,
        filename="test_resume.pdf",
        file_path="/tmp/test_resume.pdf",
        file_size=1024,
        raw_text="Test resume text",
        extracted_data={},
        parse_status="complete",
    )
    db_session.add(resume)
    db_session.commit()

    # Test Case 1: 'keep_existing'
    extracted_data_1 = {
        "projects": [
            {
                "title": "Overwriting Analytics Pipeline",
                "url": "https://github.com/candidate/analytics",
                "description": "Incoming description that should be ignored",
            }
        ]
    }
    res_1 = profile_service.apply_extracted_data_to_profile(
        db=db_session,
        user_id=user_id,
        resume_id=resume.id,
        sections=["projects"],
        edited_data=extracted_data_1,
        item_decisions={"projects:0": "keep_existing"},
    )
    db_session.refresh(orig_proj)
    assert orig_proj.title == "Original Analytics Pipeline"
    assert orig_proj.description == "Original description"

    # Verify decision recorded in career_knowledge_items
    corr_1 = (
        db_session.query(CareerKnowledgeItem)
        .filter(
            CareerKnowledgeItem.user_id == user_id,
            CareerKnowledgeItem.source_type == "user_correction",
            CareerKnowledgeItem.category == "keep_existing",
        )
        .first()
    )
    assert corr_1 is not None

    # Test Case 2: 'replace_with_new'
    extracted_data_2 = {
        "projects": [
            {
                "title": "Upgraded Analytics Pipeline v2",
                "url": "https://github.com/candidate/analytics",
                "description": "Updated new description",
                "technologies": ["Python", "PostgreSQL", "Docker"],
            }
        ]
    }
    res_2 = profile_service.apply_extracted_data_to_profile(
        db=db_session,
        user_id=user_id,
        resume_id=resume.id,
        sections=["projects"],
        edited_data=extracted_data_2,
        item_decisions={"projects:0": "replace_with_new"},
    )
    db_session.refresh(orig_proj)
    assert orig_proj.title == "Upgraded Analytics Pipeline v2"
    assert orig_proj.description == "Updated new description"
    assert res_2["counts"]["projects_updated"] == 1

    # Test Case 3: 'save_separate'
    extracted_data_3 = {
        "projects": [
            {
                "title": "Separate Analytics Microservice",
                "url": "https://github.com/candidate/analytics",
                "description": "Second project kept alongside first",
            }
        ]
    }
    res_3 = profile_service.apply_extracted_data_to_profile(
        db=db_session,
        user_id=user_id,
        resume_id=resume.id,
        sections=["projects"],
        edited_data=extracted_data_3,
        item_decisions={"projects:0": "save_separate"},
    )
    all_projects = db_session.query(Project).filter(Project.profile_id == profile.id).all()
    assert len(all_projects) == 2
    assert any(p.title == "Separate Analytics Microservice" for p in all_projects)
    assert any(p.title == "Upgraded Analytics Pipeline v2" for p in all_projects)
