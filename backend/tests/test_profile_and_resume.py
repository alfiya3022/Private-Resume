import io
import fitz
import pytest
from app.services.pdf_service import pdf_service


def create_synthetic_resume_pdf() -> bytes:
    """Generates an in-memory valid resume PDF using PyMuPDF for testing."""
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "ALICE CANDIDATE\n"
        "alice@example.com | (555) 019-2834 | San Francisco, CA\n\n"
        "SUMMARY\n"
        "Senior Software Engineer with 6+ years of experience designing scalable backends and modern web apps.\n\n"
        "TECHNICAL SKILLS\n"
        "Python, FastAPI, React, TypeScript, PostgreSQL, Docker, Git, AWS, Tailwind\n\n"
        "WORK EXPERIENCE\n"
        "CloudScale Inc - Lead Backend Engineer (2022 - Present)\n"
        "- Architected high-throughput REST APIs handling 50k requests/min\n"
        "- Containerized legacy applications using Docker and Linux\n\n"
        "KEY PROJECTS\n"
        "DataBridge Pipeline\n"
        "- Streamlined ETL workloads with Python and SQL\n\n"
        "EDUCATION\n"
        "Bachelor of Science in Computer Science - Tech University (2018)\n\n"
        "CERTIFICATIONS\n"
        "AWS Certified Solutions Architect (2023)\n"
    )
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def get_auth_token(client, email="candidate_profile@test.local"):
    """Helper to register and login a test user, returning bearer token."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123", "full_name": "Test Candidate"},
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123"},
    )
    return res.json()["access_token"]


def test_pdf_service_text_and_sections():
    """Unit test: PyMuPDF extracts text and segments sections correctly."""
    pdf_bytes = create_synthetic_resume_pdf()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    doc.close()
    
    assert "ALICE CANDIDATE" in text
    sections = pdf_service.segment_sections(text)
    assert "summary" in sections or "header" in sections
    assert "skills" in sections
    assert "experience" in sections
    assert "projects" in sections
    assert "education" in sections


def test_pdf_service_deterministic_skill_detection():
    """Unit test: detects known technical skills without hallucinations."""
    sample = "We use Python, Docker, PostgreSQL, and React with Tailwind CSS."
    skills = pdf_service.detect_skills_deterministically(sample)
    assert "Python" in skills
    assert "Docker" in skills
    assert "Postgresql" in skills or "PostgreSQL" in skills
    assert "React" in skills
    assert "Tailwind" in skills
    assert "Rust" not in skills  # Unmentioned skill not detected


def test_get_and_update_profile(client):
    """API test: retrieve auto-initialized profile and update metadata."""
    token = get_auth_token(client, "profile_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # Initial profile lookup
    get_res = client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 200
    profile = get_res.json()
    assert profile["headline"] is None

    # Update profile metadata
    update_payload = {
        "headline": "Senior Full-Stack Engineer",
        "summary": "Building resilient systems with Python and React.",
        "phone": "+1-555-0199",
        "location": "Remote, US",
        "github_url": "https://github.com/alice",
    }
    put_res = client.put("/api/v1/profile", headers=headers, json=update_payload)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["headline"] == "Senior Full-Stack Engineer"
    assert updated["location"] == "Remote, US"
    assert updated["github_url"] == "https://github.com/alice"


def test_profile_subitems_crud(client):
    """API test: CRUD operations for skills, projects, experiences, educations, certifications."""
    token = get_auth_token(client, "subitems_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Add and delete Skill
    skill_res = client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"name": "FastAPI", "category": "Framework", "proficiency": "Expert"},
    )
    assert skill_res.status_code == 201
    skill_id = skill_res.json()["id"]

    # 2. Add and delete Project
    proj_res = client.post(
        "/api/v1/profile/projects",
        headers=headers,
        json={
            "title": "PrivateResume Engine",
            "role": "Creator",
            "bullets": ["Engineered local LLM prompt flow"],
            "technologies": ["Python", "FastAPI"],
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 3. Add Experience
    exp_res = client.post(
        "/api/v1/profile/experiences",
        headers=headers,
        json={
            "company": "Acme Labs",
            "title": "Software Engineer",
            "bullets": ["Delivered backend features"],
            "is_current": True,
        },
    )
    assert exp_res.status_code == 201
    exp_id = exp_res.json()["id"]

    # 4. Verify items exist in profile
    profile_res = client.get("/api/v1/profile", headers=headers)
    assert len(profile_res.json()["skills"]) == 1
    assert len(profile_res.json()["projects"]) == 1
    assert len(profile_res.json()["experiences"]) == 1

    # 5. Delete items
    assert client.delete(f"/api/v1/profile/skills/{skill_id}", headers=headers).status_code == 204
    assert client.delete(f"/api/v1/profile/projects/{proj_id}", headers=headers).status_code == 204
    assert client.delete(f"/api/v1/profile/experiences/{exp_id}", headers=headers).status_code == 204

    # 6. Verify items deleted
    clean_profile = client.get("/api/v1/profile", headers=headers).json()
    assert len(clean_profile["skills"]) == 0
    assert len(clean_profile["projects"]) == 0
    assert len(clean_profile["experiences"]) == 0


def test_upload_master_resume_pdf(client):
    """API test: upload PDF master resume, verify parsing and auto-skill extraction."""
    token = get_auth_token(client, "resume_upload@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    pdf_content = create_synthetic_resume_pdf()
    files = {"file": ("master_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

    response = client.post("/api/v1/resumes", headers=headers, files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "master_resume.pdf"
    assert data["file_size"] > 0
    assert "Python" in data["extracted_skills"]
    assert "FastAPI" in data["extracted_skills"]
    resume_id = data["resume_id"]

    # Verify resume listed
    resumes_res = client.get("/api/v1/resumes", headers=headers)
    assert resumes_res.status_code == 200
    assert len(resumes_res.json()) == 1
    assert resumes_res.json()[0]["id"] == resume_id

    # Verify profile skills auto-populated
    profile_res = client.get("/api/v1/profile", headers=headers)
    assert len(profile_res.json()["skills"]) >= 3

    # Delete master resume
    del_res = client.delete(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert del_res.status_code == 204


def test_upload_non_pdf_fails(client):
    """Negative API test: reject non-PDF file upload with 400 Bad Request."""
    token = get_auth_token(client, "bad_file_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("malicious.exe", io.BytesIO(b"binary content"), "application/octet-stream")}
    response = client.post("/api/v1/resumes", headers=headers, files=files)
    assert response.status_code == 400
    assert "only pdf files" in response.json()["detail"].lower()


def test_upload_empty_pdf_fails(client):
    """Negative API test: reject 0-byte file upload with 400 Bad Request."""
    token = get_auth_token(client, "empty_file_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
    response = client.post("/api/v1/resumes", headers=headers, files=files)
    assert response.status_code == 400
    assert "file is empty" in response.json()["detail"].lower()


def test_profile_and_resume_user_isolation(client):
    """Security test: User 1 cannot access, modify, or delete User 2's profile or master resume."""
    token1 = get_auth_token(client, "user_iso_1@test.local")
    token2 = get_auth_token(client, "user_iso_2@test.local")
    h1 = {"Authorization": f"Bearer {token1}"}
    h2 = {"Authorization": f"Bearer {token2}"}

    # User 1 adds a skill and uploads a resume
    s1 = client.post("/api/v1/profile/skills", headers=h1, json={"name": "Rust"}).json()
    pdf_content = create_synthetic_resume_pdf()
    r1 = client.post(
        "/api/v1/resumes",
        headers=h1,
        files={"file": ("u1.pdf", io.BytesIO(pdf_content), "application/pdf")},
    ).json()

    # User 2 attempts to delete User 1's skill -> 404
    del_skill = client.delete(f"/api/v1/profile/skills/{s1['id']}", headers=h2)
    assert del_skill.status_code == 404

    # User 2 attempts to delete User 1's resume -> 404
    del_resume = client.delete(f"/api/v1/resumes/{r1['resume_id']}", headers=h2)
    assert del_resume.status_code == 404

    # User 2's resume list must not show User 1's resume
    u2_resumes = client.get("/api/v1/resumes", headers=h2).json()
    assert len(u2_resumes) == 0
