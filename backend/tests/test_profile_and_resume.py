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


def test_extract_github_project(client):
    """Test extracting project details from a GitHub URL."""
    token = get_auth_token(client, "github_test@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/v1/profile/projects/extract-github",
        headers=headers,
        json={"github_url": "https://github.com/torvalds/linux"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "title" in data
    assert "url" in data
    assert "bullets" in data
    assert isinstance(data["bullets"], list)


def test_single_master_resume_enforcement_and_replacement(client):
    """Verify single Master Resume PDF constraint per user: reject duplicate upload, allow in-place replacement and post-delete upload."""
    token = get_auth_token(client, "single_resume_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    pdf1 = create_synthetic_resume_pdf()
    files1 = {"file": ("first_resume.pdf", io.BytesIO(pdf1), "application/pdf")}

    # 1. First upload succeeds
    res1 = client.post("/api/v1/resumes", headers=headers, files=files1)
    assert res1.status_code == 201
    r1_data = res1.json()
    r1_id = r1_data["resume_id"]
    assert r1_data["filename"] == "first_resume.pdf"

    # Verify exactly 1 resume in list
    list_res1 = client.get("/api/v1/resumes", headers=headers)
    assert list_res1.status_code == 200
    assert len(list_res1.json()) == 1

    # 2. Second upload WITHOUT replace flag is rejected with 400 Bad Request
    pdf2 = create_synthetic_resume_pdf()
    files2 = {"file": ("second_resume.pdf", io.BytesIO(pdf2), "application/pdf")}
    res2 = client.post("/api/v1/resumes", headers=headers, files=files2)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()

    # Verify list still contains only 1 resume
    list_res2 = client.get("/api/v1/resumes", headers=headers)
    assert len(list_res2.json()) == 1

    # 3. Upload WITH replace=true replaces the existing master resume in-place
    files3 = {"file": ("replaced_resume.pdf", io.BytesIO(pdf2), "application/pdf")}
    res3 = client.post("/api/v1/resumes?replace=true", headers=headers, files=files3)
    assert res3.status_code == 201
    r3_data = res3.json()
    assert r3_data["filename"] == "replaced_resume.pdf"

    # Verify exactly 1 resume exists in DB and list
    list_res3 = client.get("/api/v1/resumes", headers=headers)
    resumes = list_res3.json()
    assert len(resumes) == 1
    assert resumes[0]["filename"] == "replaced_resume.pdf"

    # 4. Deleting the existing master resume allows a subsequent upload
    del_res = client.delete(f"/api/v1/resumes/{resumes[0]['id']}", headers=headers)
    assert del_res.status_code == 204

    list_res_empty = client.get("/api/v1/resumes", headers=headers)
    assert len(list_res_empty.json()) == 0

    # 5. Subsequent upload now succeeds without needing replace flag
    pdf4 = create_synthetic_resume_pdf()
    files4 = {"file": ("fresh_resume.pdf", io.BytesIO(pdf4), "application/pdf")}
    res4 = client.post("/api/v1/resumes", headers=headers, files=files4)
    assert res4.status_code == 201
    assert res4.json()["filename"] == "fresh_resume.pdf"

    list_res4 = client.get("/api/v1/resumes", headers=headers)
    assert len(list_res4.json()) == 1


def test_reset_individual_profile_sections(client):
    """Test resetting each profile section individually deletes persisted records without affecting other sections."""
    token = get_auth_token(client, "reset_sections_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Populate all sections
    client.put("/api/v1/profile", headers=headers, json={
        "headline": "Lead Engineer",
        "summary": "Experienced architect",
        "phone": "+1 555 1234",
        "location": "Boston, MA",
        "linkedin_url": "https://linkedin.com/in/testlead",
    })
    client.post("/api/v1/profile/skills", headers=headers, json={"name": "Python", "category": "Languages"})
    client.post("/api/v1/profile/skills", headers=headers, json={"name": "PostgreSQL", "category": "Databases"})
    client.post("/api/v1/profile/projects", headers=headers, json={"title": "Cloud Manager", "technologies": ["Python"]})
    client.post("/api/v1/profile/experiences", headers=headers, json={"company": "Acme Inc", "title": "Senior Dev"})
    client.post("/api/v1/profile/educations", headers=headers, json={"institution": "MIT", "degree": "BS CS"})
    client.post("/api/v1/profile/certifications", headers=headers, json={"name": "AWS Certified", "issuer": "Amazon"})

    prof_before = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof_before["skills"]) == 2
    assert len(prof_before["projects"]) == 1
    assert len(prof_before["experiences"]) == 1
    assert len(prof_before["educations"]) == 1
    assert len(prof_before["certifications"]) == 1
    assert prof_before["headline"] == "Lead Engineer"

    # 2. Reset Skills section
    res_skills = client.delete("/api/v1/profile/sections/skills", headers=headers)
    assert res_skills.status_code == 200
    prof = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof["skills"]) == 0
    # Other sections untouched
    assert len(prof["projects"]) == 1
    assert len(prof["experiences"]) == 1
    assert prof["headline"] == "Lead Engineer"

    # 3. Reset Projects section
    res_proj = client.delete("/api/v1/profile/sections/projects", headers=headers)
    assert res_proj.status_code == 200
    prof = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof["projects"]) == 0
    assert len(prof["experiences"]) == 1

    # 4. Reset Experience section
    res_exp = client.delete("/api/v1/profile/sections/experience", headers=headers)
    assert res_exp.status_code == 200
    prof = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof["experiences"]) == 0
    assert len(prof["educations"]) == 1

    # 5. Reset Education section
    res_edu = client.delete("/api/v1/profile/sections/education", headers=headers)
    assert res_edu.status_code == 200
    prof = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof["educations"]) == 0
    assert len(prof["certifications"]) == 1

    # 6. Reset Certifications section
    res_cert = client.delete("/api/v1/profile/sections/certifications", headers=headers)
    assert res_cert.status_code == 200
    prof = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof["certifications"]) == 0
    assert prof["headline"] == "Lead Engineer"

    # 7. Reset Personal Info section
    res_pers = client.delete("/api/v1/profile/sections/personal", headers=headers)
    assert res_pers.status_code == 200
    prof = client.get("/api/v1/profile", headers=headers).json()
    assert prof["headline"] is None
    assert prof["summary"] is None
    assert prof["phone"] is None
    assert prof["location"] is None
    assert prof["linkedin_url"] is None


def test_reset_all_profile_preserves_master_resume(client):
    """Test Reset All clears all 6 profile sections in an atomic transaction while keeping Master Resume PDF intact."""
    token = get_auth_token(client, "reset_all_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # Upload Master Resume PDF
    pdf_bytes = create_synthetic_resume_pdf()
    files = {"file": ("my_master_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    res_upload = client.post("/api/v1/resumes", headers=headers, files=files)
    assert res_upload.status_code == 201

    # Populate all 6 sections
    client.put("/api/v1/profile", headers=headers, json={"headline": "Full-Stack Dev", "summary": "Great summary"})
    client.post("/api/v1/profile/skills", headers=headers, json={"name": "Docker", "category": "DevOps"})
    client.post("/api/v1/profile/projects", headers=headers, json={"title": "Private Resume App"})
    client.post("/api/v1/profile/experiences", headers=headers, json={"company": "Tech Corp", "title": "Staff SWE"})
    client.post("/api/v1/profile/educations", headers=headers, json={"institution": "Stanford", "degree": "MS"})
    client.post("/api/v1/profile/certifications", headers=headers, json={"name": "Kubernetes Admin", "issuer": "CNCF"})

    prof_before = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof_before["skills"]) >= 1
    assert len(prof_before["projects"]) >= 1
    assert len(prof_before["experiences"]) >= 1
    assert len(prof_before["educations"]) >= 1
    assert len(prof_before["certifications"]) >= 1
    assert prof_before["headline"] == "Full-Stack Dev"

    # Call Reset All endpoint
    res_reset_all = client.delete("/api/v1/profile/reset-all", headers=headers)
    assert res_reset_all.status_code == 200
    reset_data = res_reset_all.json()
    assert reset_data["headline"] is None
    assert reset_data["summary"] is None
    assert len(reset_data["skills"]) == 0
    assert len(reset_data["projects"]) == 0
    assert len(reset_data["experiences"]) == 0
    assert len(reset_data["educations"]) == 0
    assert len(reset_data["certifications"]) == 0

    # Fresh profile reload confirms all 6 sections remain at zero
    fresh_prof = client.get("/api/v1/profile", headers=headers).json()
    assert fresh_prof["headline"] is None
    assert fresh_prof["summary"] is None
    assert len(fresh_prof["skills"]) == 0
    assert len(fresh_prof["projects"]) == 0
    assert len(fresh_prof["experiences"]) == 0
    assert len(fresh_prof["educations"]) == 0
    assert len(fresh_prof["certifications"]) == 0

    # Verify Master Resume is STILL INTACT and NOT deleted
    resumes_list = client.get("/api/v1/resumes", headers=headers).json()
    assert len(resumes_list) == 1
    assert resumes_list[0]["filename"] == "my_master_resume.pdf"


def test_reset_user_isolation(client):
    """Test resetting profile for User A does not delete or mutate User B's profile records."""
    token_a = get_auth_token(client, "user_a@test.local")
    token_b = get_auth_token(client, "user_b@test.local")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A data
    client.put("/api/v1/profile", headers=headers_a, json={"headline": "User A Headline"})
    client.post("/api/v1/profile/skills", headers=headers_a, json={"name": "Rust"})

    # User B data
    client.put("/api/v1/profile", headers=headers_b, json={"headline": "User B Headline"})
    client.post("/api/v1/profile/skills", headers=headers_b, json={"name": "Go"})

    # User A resets all
    client.delete("/api/v1/profile/reset-all", headers=headers_a)

    prof_a = client.get("/api/v1/profile", headers=headers_a).json()
    assert prof_a["headline"] is None
    assert len(prof_a["skills"]) == 0

    # User B data remains completely intact
    prof_b = client.get("/api/v1/profile", headers=headers_b).json()
    assert prof_b["headline"] == "User B Headline"
    assert len(prof_b["skills"]) == 1
    assert prof_b["skills"][0]["name"] == "Go"


def test_apply_extracted_projects_deduplication(client, db_session):
    """Test that applying extracted project list twice leaves one project,
    and a project with slightly different title (e.g. 'Private Resume' vs 'Private Resume [GitHub]') is not duplicated.
    """
    token = get_auth_token(client, "project_dedup_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Upload a synthetic resume
    pdf_content = create_synthetic_resume_pdf()
    res = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": ("dedup_resume.pdf", io.BytesIO(pdf_content), "application/pdf")},
    )
    assert res.status_code == 201
    resume_id = res.json()["resume_id"]

    # Mock extracted data on the resume with project "Private Resume"
    from app.models.resume import MasterResume
    resume = db_session.query(MasterResume).filter(MasterResume.id == resume_id).first()
    resume.extracted_data = {
        "projects": [
            {
                "title": "Private Resume",
                "description": "Local AI resume tailoring app",
                "technologies": ["Python", "FastAPI", "React"],
                "bullets": ["Engineered secure local extraction"],
            }
        ]
    }
    db_session.commit()

    # Apply project section first time
    apply_res1 = client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json={"sections": ["projects"], "overwrite_existing": False},
    )
    assert apply_res1.status_code == 200
    assert apply_res1.json()["counts"]["projects_added"] == 1

    # Check profile has 1 project
    prof1 = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof1["projects"]) == 1
    assert prof1["projects"][0]["title"] == "Private Resume"

    # Apply same extracted project list again -> must skip and leave 1 project
    apply_res2 = client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json={"sections": ["projects"], "overwrite_existing": False},
    )
    assert apply_res2.status_code == 200
    assert apply_res2.json()["counts"]["projects_added"] == 0

    prof2 = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof2["projects"]) == 1

    # Now update extracted_data to have slightly different title: "Private Resume [GitHub]"
    resume = db_session.query(MasterResume).filter(MasterResume.id == resume_id).first()
    resume.extracted_data = {
        "projects": [
            {
                "title": "Private Resume [GitHub]",
                "description": "Local AI resume tailoring app with GitHub badge",
                "technologies": ["Python", "FastAPI", "React"],
                "bullets": ["Engineered secure local extraction"],
            }
        ]
    }
    db_session.commit()

    # Apply project section again with slightly different title -> must NOT duplicate
    apply_res3 = client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json={"sections": ["projects"], "overwrite_existing": False},
    )
    assert apply_res3.status_code == 200
    assert apply_res3.json()["counts"]["projects_added"] == 0

    prof3 = client.get("/api/v1/profile", headers=headers).json()
    assert len(prof3["projects"]) == 1




