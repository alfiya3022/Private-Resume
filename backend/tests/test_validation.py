import pytest
from fastapi.testclient import TestClient


def setup_candidate_and_job(client: TestClient, email: str, name: str):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!", "full_name": name},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.put(
        "/api/v1/profile",
        json={
            "headline": "Lead Systems Architect",
            "phone": "555-018-9999",
            "location": "San Francisco, CA",
            "summary": "Experienced engineer with a focus on scalable distributed systems.",
        },
        headers=headers,
    )

    client.post(
        "/api/v1/profile/skills",
        json={"name": "Python", "category": "Language", "proficiency": "Expert"},
        headers=headers,
    )

    client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Nexus Systems",
            "title": "Principal Architect",
            "location": "San Francisco, CA",
            "start_date": "2020",
            "end_date": "Present",
            "bullets": ["Architected distributed event streaming backend handling 50k events/sec."],
        },
        headers=headers,
    )

    client.post(
        "/api/v1/profile/education",
        json={
            "institution": "University of California, Berkeley",
            "degree": "B.S. in Computer Science",
            "year": "2019",
        },
        headers=headers,
    )

    job_res = client.post(
        "/api/v1/jobs",
        json={
            "company": "TechStream",
            "title": "Principal Engineer",
            "raw_jd_text": "Looking for Principal Engineer with Python and distributed systems expertise.",
        },
        headers=headers,
    )
    job_id = job_res.json()["id"]

    tailor_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = tailor_res.json()["id"]

    return headers, resume_id


def test_validation_requires_compiled_pdf(client: TestClient):
    headers, resume_id = setup_candidate_and_job(
        client, "uncompiled_user@test.local", "Uncompiled User"
    )

    # Calling validation prior to PDF generation should fail with 400
    res = client.post(f"/api/v1/tailored-resumes/{resume_id}/validate", headers=headers)
    assert res.status_code == 400
    assert "Compiled PDF not found" in res.json()["detail"]


def test_successful_validation_and_report_retrieval(client: TestClient):
    headers, resume_id = setup_candidate_and_job(
        client, "valid_ats_user@test.local", "Valid ATS Candidate"
    )

    # 1. Compile PDF
    gen_res = client.post(
        f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=headers
    )
    assert gen_res.status_code == 200

    # 2. Run ATS validation
    val_res = client.post(
        f"/api/v1/tailored-resumes/{resume_id}/validate", headers=headers
    )
    assert val_res.status_code == 200
    report = val_res.json()

    assert report["tailored_resume_id"] == resume_id
    assert report["overall_status"] in ["PASS", "WARN"]
    assert report["score"] >= 80

    checks = report["checks"]
    assert "pdf_generation" in checks
    assert checks["pdf_generation"]["status"] == "PASS"

    assert "text_extractability" in checks
    assert checks["text_extractability"]["status"] == "PASS"

    assert "contact_details" in checks
    assert checks["contact_details"]["status"] == "PASS"

    assert "standard_headings" in checks
    assert checks["standard_headings"]["status"] in ["PASS", "WARN"]

    assert "placeholders" in checks
    assert checks["placeholders"]["status"] == "PASS"

    assert "integrity_audit" in checks
    assert checks["integrity_audit"]["status"] == "PASS"

    # 3. Retrieve validation via GET
    get_res = client.get(
        f"/api/v1/tailored-resumes/{resume_id}/validation", headers=headers
    )
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == report["id"]
    assert retrieved["overall_status"] == report["overall_status"]


def test_validation_user_isolation(client: TestClient):
    headers_a, resume_id_a = setup_candidate_and_job(
        client, "user_a_ats@test.local", "User A ATS"
    )

    # Compile for User A
    client.post(f"/api/v1/tailored-resumes/{resume_id_a}/generate-pdf", headers=headers_a)
    client.post(f"/api/v1/tailored-resumes/{resume_id_a}/validate", headers=headers_a)

    # Register User B
    client.post(
        "/api/v1/auth/register",
        json={"email": "user_b_ats@test.local", "password": "SecurePassword123!", "full_name": "User B"},
    )
    login_b = client.post(
        "/api/v1/auth/login",
        json={"email": "user_b_ats@test.local", "password": "SecurePassword123!"},
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    # User B cannot validate User A's resume
    post_res = client.post(f"/api/v1/tailored-resumes/{resume_id_a}/validate", headers=headers_b)
    assert post_res.status_code == 404

    # User B cannot read User A's validation
    get_res = client.get(f"/api/v1/tailored-resumes/{resume_id_a}/validation", headers=headers_b)
    assert get_res.status_code == 404
