import pytest
from app.services.ai.ollama_provider import ollama_provider


def get_auth_token(client, email="jd_user@test.local"):
    """Helper to authenticate a test user and obtain bearer token."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password12345", "full_name": "JD User"},
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password12345"},
    )
    return res.json()["access_token"]


def test_ollama_provider_deterministic_extraction():
    """Unit test: verify deterministic requirement extraction from raw JD text."""
    sample_jd = (
        "Role: Senior Full Stack Engineer\n"
        "Experience: 5+ years of software engineering experience.\n"
        "Responsibilities:\n"
        "- Build scalable microservices and REST APIs using FastAPI and Python\n"
        "- Develop interactive web interfaces with React and Tailwind CSS\n"
        "- Manage relational database schemas with PostgreSQL\n"
        "Qualifications:\n"
        "- BS or MS in Computer Science or equivalent practical experience\n"
        "- Proficiency with Docker, Git, and AWS cloud services\n"
        "- Strong written and verbal communication skills\n"
    )

    analysis = ollama_provider.deterministic_jd_extraction(sample_jd)
    assert "Python" in analysis.languages
    assert "FastAPI" in analysis.frameworks
    assert "React" in analysis.frameworks
    assert "PostgreSQL" in analysis.databases
    assert "Docker" in analysis.tools
    assert "AWS" in analysis.cloud
    assert "5+ Years" in analysis.experience_years
    assert len(analysis.responsibilities) > 0
    assert len(analysis.qualifications) > 0
    assert "Communication" in analysis.soft_skills


def test_analyze_job_and_retrieve_analysis(client):
    """API test: trigger job analysis and retrieve persisted requirements."""
    token = get_auth_token(client, "analysis_candidate@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a job
    job_payload = {
        "company": "CloudTech Systems",
        "title": "Backend Python Developer",
        "raw_jd_text": (
            "We are looking for a Backend Developer with 4+ years of experience.\n"
            "Responsibilities:\n"
            "- Implement high-performance backend services in Python and FastAPI\n"
            "- Design data storage layers in PostgreSQL and Redis\n"
            "Requirements:\n"
            "- Proficient with Docker, Git, and Linux environments\n"
            "- Excellent teamwork and problem solving abilities\n"
        ),
    }
    job = client.post("/api/v1/jobs", headers=headers, json=job_payload).json()
    job_id = job["id"]

    # 2. Trigger analysis
    analyze_res = client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    assert data["job_id"] == job_id
    assert "Python" in data["languages"]
    assert "FastAPI" in data["frameworks"]
    assert "PostgreSQL" in data["databases"]
    assert "Docker" in data["tools"]
    assert len(data["required_skills"]) > 0

    # 3. Retrieve existing analysis via GET
    get_res = client.get(f"/api/v1/jobs/{job_id}/analysis", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == data["id"]
    assert get_res.json()["job_id"] == job_id


def test_analyze_nonexistent_job_fails(client):
    """Negative API test: 404 when analyzing non-existent job."""
    token = get_auth_token(client, "missing_job_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/jobs/99999/analyze", headers=headers)
    assert res.status_code == 404


def test_job_analysis_user_isolation(client):
    """Security test: User 1 analysis cannot be read or triggered by User 2."""
    t1 = get_auth_token(client, "user_ana_1@test.local")
    t2 = get_auth_token(client, "user_ana_2@test.local")
    h1 = {"Authorization": f"Bearer {t1}"}
    h2 = {"Authorization": f"Bearer {t2}"}

    job = client.post(
        "/api/v1/jobs",
        headers=h1,
        json={"company": "Secret AI", "title": "AI Engineer", "raw_jd_text": "Python and PyTorch required"},
    ).json()
    job_id = job["id"]

    # User 1 analyzes job
    client.post(f"/api/v1/jobs/{job_id}/analyze", headers=h1)

    # User 2 attempts to retrieve User 1 analysis -> 404
    assert client.get(f"/api/v1/jobs/{job_id}/analysis", headers=h2).status_code == 404

    # User 2 attempts to trigger analysis on User 1 job -> 404
    assert client.post(f"/api/v1/jobs/{job_id}/analyze", headers=h2).status_code == 404
