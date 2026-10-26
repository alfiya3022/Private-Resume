import json
import logging
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.services.pdf_service import pdf_service

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REF_PDF_PATH = FIXTURES_DIR / "master_resume_reference.pdf"
REF_EXPECTED_PATH = FIXTURES_DIR / "master_resume_reference.expected.json"


def get_auth_token(client: TestClient, email: str = "extraction_test@local.dev") -> str:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecureTestPassword123!", "full_name": "Test User"},
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecureTestPassword123!"},
    )
    return res.json()["access_token"]


def test_async_master_resume_upload_returns_202_queued(client: TestClient):
    """POST /api/v1/resumes returns HTTP 202 with queued parse status."""
    token = get_auth_token(client, "async_upload_202@local.dev")
    headers = {"Authorization": f"Bearer {token}"}

    pdf_bytes = REF_PDF_PATH.read_bytes()
    files = {"file": ("master_resume_reference.pdf", pdf_bytes, "application/pdf")}

    response = client.post("/api/v1/resumes", headers=headers, files=files)
    assert response.status_code == 202
    data = response.json()
    assert "queued for background extraction" in data["message"]
    assert data["parse_status"] == "queued"
    assert "resume_id" in data
    assert data["filename"] == "master_resume_reference.pdf"


def test_poll_resume_status_lifecycle(client: TestClient):
    """GET /api/v1/resumes/{resume_id}/status returns the real status and stage."""
    token = get_auth_token(client, "poll_status@local.dev")
    headers = {"Authorization": f"Bearer {token}"}

    pdf_bytes = REF_PDF_PATH.read_bytes()
    files = {"file": ("master_resume_reference.pdf", pdf_bytes, "application/pdf")}

    upload_res = client.post("/api/v1/resumes", headers=headers, files=files)
    assert upload_res.status_code == 202
    resume_id = upload_res.json()["resume_id"]

    status_res = client.get(f"/api/v1/resumes/{resume_id}/status", headers=headers)
    assert status_res.status_code == 200
    st_data = status_res.json()
    assert st_data["resume_id"] == resume_id
    assert st_data["parse_status"] in ["queued", "running", "complete"]
    assert st_data["parse_stage"] is not None


def test_master_resume_reference_full_extraction_accuracy():
    """Verify deterministic layout-aware extraction on master_resume_reference.pdf against ground truth."""
    assert REF_PDF_PATH.exists()
    assert REF_EXPECTED_PATH.exists()

    expected = json.loads(REF_EXPECTED_PATH.read_text(encoding="utf-8"))
    extracted = pdf_service.extract_full_resume_data(str(REF_PDF_PATH))

    # 1. Personal Info
    pinfo = extracted["personal_info"]
    exp_pinfo = expected["personal_info"]
    assert pinfo["name"] == exp_pinfo["name"]
    assert pinfo["email"] == exp_pinfo["email"]
    assert pinfo["phone"] == exp_pinfo["phone"]
    assert pinfo["location"] == exp_pinfo["location"]
    assert pinfo["headline"] == exp_pinfo["headline"]
    assert pinfo["github_url"] == exp_pinfo["github_url"]
    assert pinfo["linkedin_url"] == exp_pinfo["linkedin_url"]

    # 2. Education
    assert len(extracted["education"]) >= 1
    edu = extracted["education"][0]
    exp_edu = expected["education"][0]
    assert exp_edu["degree"].lower() in edu["degree"].lower()
    assert exp_edu["institution"].lower() in edu["institution"].lower()
    assert exp_edu["grade"] in edu["grade"]
    assert edu["grade_type"] == exp_edu["grade_type"]

    # 3. Projects
    assert len(extracted["projects"]) == len(expected["projects"])
    for exp_p, act_p in zip(expected["projects"], extracted["projects"]):
        assert exp_p["title"].lower() in act_p["title"].lower()
        assert act_p["url"] == exp_p["url"]
        for tech in exp_p["technologies"]:
            assert any(tech.lower() in t.lower() for t in act_p["technologies"])

    # 4. Experience
    assert len(extracted["experience"]) >= 1
    exp = extracted["experience"][0]
    exp_exp = expected["experience"][0]
    assert exp_exp["company"].lower() in exp["company"].lower()
    assert exp_exp["title"].lower() in exp["title"].lower()

    # 5. Certifications & Achievements
    assert len(extracted["certifications"]) >= 4
    act_cert_names = [c["name"].lower() for c in extracted["certifications"]]
    for exp_c in expected["certifications"]:
        assert any(exp_c["name"].lower() in name for name in act_cert_names)

    # 6. Complete Skills Inventory (36/36)
    expected_skills = expected.get("expected_skills", [])
    extracted_skills = extracted["skills"]
    extracted_skill_names = {s["name"].lower() if isinstance(s, dict) else str(s).lower() for s in extracted_skills}

    missing_skills = [s for s in expected_skills if s.lower() not in extracted_skill_names]
    assert len(missing_skills) == 0, f"Missing deterministic skills: {missing_skills}"


def test_semantic_prototypes_and_custom_section_preservation():
    """Verify semantic section categorization preserves non-standard sections in custom_sections."""
    doc_lines = [
        {"text": "VOLUNTEERING & COMMUNITY OUTREACH", "is_bold": True, "max_size": 13.0, "links": []},
        {"text": "Organized annual technical literacy workshops for 200+ students.", "is_bold": False, "max_size": 10.0, "links": []},
        {"text": "PUBLICATIONS", "is_bold": True, "max_size": 13.0, "links": []},
        {"text": "Shaikh, A. Deep learning multi-exposure image fusion. IEEE Conference, 2025.", "is_bold": False, "max_size": 10.0, "links": []},
    ]

    sections = pdf_service.segment_sections(raw_text="", layout_lines=doc_lines)
    standard_keys = {"header", "summary", "skills", "experience", "projects", "education", "certifications"}
    custom_sections = {k: v for k, v in sections.items() if k not in standard_keys}

    assert any("volunteering" in k.lower() for k in custom_sections.keys())
    assert any("publications" in k.lower() for k in custom_sections.keys())


def test_apply_extracted_data_to_profile_duplicate_handling(client: TestClient):
    """User-controlled duplicate handling: overwrite_existing=False preserves existing records; True updates them."""
    token = get_auth_token(client, "duplicate_ctrl@local.dev")
    headers = {"Authorization": f"Bearer {token}"}

    # First add an existing project manually without a URL and with 1 tech
    client.post(
        "/api/v1/profile/projects",
        headers=headers,
        json={
            "title": "Investment Portfolio Analytics & Trade Data Warehouse",
            "description": "Original manual description",
            "technologies": ["SQL"],
        },
    )

    # Upload reference resume
    pdf_bytes = REF_PDF_PATH.read_bytes()
    files = {"file": ("master_resume_reference.pdf", pdf_bytes, "application/pdf")}
    upload_res = client.post("/api/v1/resumes", headers=headers, files=files)
    assert upload_res.status_code == 202
    resume_id = upload_res.json()["resume_id"]

    # 1. Apply with overwrite_existing=False -> does NOT overwrite technologies or URL
    apply_res_false = client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json={"sections": ["projects"], "overwrite_existing": False},
    )
    assert apply_res_false.status_code == 200
    prof_after_false = client.get("/api/v1/profile", headers=headers).json()
    proj_after_false = next(p for p in prof_after_false["projects"] if "Investment" in p["title"])
    assert proj_after_false["technologies"] == ["SQL"]
    assert not proj_after_false["url"]

    # 2. Apply with overwrite_existing=True -> updates with parsed resume technologies and URL
    apply_res_true = client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json={"sections": ["projects"], "overwrite_existing": True},
    )
    assert apply_res_true.status_code == 200
    prof_after_true = client.get("/api/v1/profile", headers=headers).json()
    proj_after_true = next(p for p in prof_after_true["projects"] if "Investment" in p["title"])
    assert len(proj_after_true["technologies"]) > 1
    assert "github.com" in proj_after_true["url"]


def test_log_sanitization_no_pii_in_logs(caplog):
    """Verify that sensitive PII (phone, email, full resume text) is not leaked into logger output."""
    caplog.set_level(logging.DEBUG)

    pdf_service.extract_full_resume_data(str(REF_PDF_PATH))

    log_text = caplog.text
    assert "+91-8080713022" not in log_text
    assert "alfiya43shaikh@gmail.com" not in log_text
