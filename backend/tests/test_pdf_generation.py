import pytest
from fastapi.testclient import TestClient
from app.services.latex_service import latex_escape


def get_auth_token(client: TestClient, email: str, name: str):
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
        json={"headline": "Senior Platform Engineer", "phone": "555-0199", "location": "Austin, TX"},
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
            "company": "Cloud Corp",
            "title": "Backend Architect",
            "location": "Austin, TX",
            "start_date": "2021",
            "end_date": "Present",
            "bullets": ["Architected distributed systems handling 100k requests."],
        },
        headers=headers,
    )

    return headers


def test_latex_special_character_escaping():
    raw_text = "C# & C++ ($100k) 50% _under_ {braces} ~tilde~ ^hat^ \\slash"
    escaped = latex_escape(raw_text)
    assert r"\#" in escaped
    assert r"\&" in escaped
    assert r"\$" in escaped
    assert r"\%" in escaped
    assert r"\_" in escaped
    assert r"\{" in escaped
    assert r"\}" in escaped
    assert r"\textasciitilde{}" in escaped
    assert r"\textasciicircum{}" in escaped


def test_pdf_compilation_and_artifact_retrieval(client: TestClient):
    headers = get_auth_token(client, "latex_user@test.local", "LaTeX Candidate")

    # Create job & tailored resume
    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "Acme Tech", "title": "Staff Engineer", "raw_jd_text": "Python and FastAPI required."},
        headers=headers,
    )
    job_id = job_res.json()["id"]

    tailor_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = tailor_res.json()["id"]

    # Generate PDF via LaTeX compiler
    pdf_res = client.post(f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=headers)
    assert pdf_res.status_code == 200
    pdf_data = pdf_res.json()
    assert pdf_data["status"] == "success"
    assert "pdf_artifact" in pdf_data
    assert pdf_data["pdf_artifact"]["artifact_type"] == "pdf"
    assert pdf_data["pdf_artifact"]["file_size"] > 0

    # Retrieve artifact list
    art_res = client.get(f"/api/v1/tailored-resumes/{resume_id}/artifacts", headers=headers)
    assert art_res.status_code == 200
    artifacts = art_res.json()
    types = [a["artifact_type"] for a in artifacts]
    assert "pdf" in types
    assert "tex" in types

    # Download / stream PDF
    stream_res = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf", headers=headers)
    assert stream_res.status_code == 200
    assert stream_res.headers["content-type"] == "application/pdf"
    assert len(stream_res.content) > 1000  # Real PDF binary bytes

    # Download TeX source
    tex_res = client.get(f"/api/v1/tailored-resumes/{resume_id}/tex", headers=headers)
    assert tex_res.status_code == 200
    assert "text/plain" in tex_res.headers["content-type"]
    assert "documentclass" in tex_res.text


def test_pdf_generation_user_isolation(client: TestClient):
    user1_headers = get_auth_token(client, "user1_pdf@test.local", "User One PDF")
    user2_headers = get_auth_token(client, "user2_pdf@test.local", "User Two PDF")

    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "Iso Corp", "title": "Dev", "raw_jd_text": "Python"},
        headers=user1_headers,
    )
    job_id = job_res.json()["id"]
    resume_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=user1_headers)
    resume_id = resume_res.json()["id"]

    # Compile for user 1
    client.post(f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=user1_headers)

    # User 2 attempts to generate PDF -> 404
    assert client.post(f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=user2_headers).status_code == 404

    # User 2 attempts to get artifacts -> 404
    assert client.get(f"/api/v1/tailored-resumes/{resume_id}/artifacts", headers=user2_headers).status_code == 404

    # User 2 attempts to stream PDF -> 404
    assert client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf", headers=user2_headers).status_code == 404
