import pytest


def get_user_token(client, email="job_candidate@test.local"):
    """Helper to authenticate a test user and obtain bearer token."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password12345", "full_name": "Job Candidate"},
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password12345"},
    )
    return res.json()["access_token"]


def test_create_job_success(client):
    """API test: create and persist target job with raw JD text."""
    token = get_user_token(client, "job_user1@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "company": "TechNova Corp",
        "title": "Senior Backend Developer",
        "location": "Remote / San Francisco",
        "job_url": "https://technova.jobs/senior-backend",
        "salary": "$150,000 - $180,000",
        "raw_jd_text": (
            "We are seeking a Senior Backend Developer with 5+ years of experience in Python and FastAPI. "
            "Must have experience designing REST APIs, PostgreSQL, Docker, and local AI workflows."
        ),
    }

    response = client.post("/api/v1/jobs", headers=headers, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "TechNova Corp"
    assert data["title"] == "Senior Backend Developer"
    assert data["status"] == "active"
    assert "id" in data
    assert "user_id" in data


def test_create_job_empty_validation(client):
    """API validation test: reject blank fields with 422."""
    token = get_user_token(client, "job_val_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # Blank title
    r1 = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"company": "Acme", "title": "   ", "raw_jd_text": "Valid text"},
    )
    assert r1.status_code == 422

    # Blank raw_jd_text
    r2 = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"company": "Acme", "title": "Engineer", "raw_jd_text": ""},
    )
    assert r2.status_code == 422


def test_list_and_get_jobs(client):
    """API test: list jobs and get single job by ID."""
    token = get_user_token(client, "job_list_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # Create two jobs
    j1 = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"company": "Company A", "title": "Title A", "raw_jd_text": "JD A"},
    ).json()

    j2 = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"company": "Company B", "title": "Title B", "raw_jd_text": "JD B"},
    ).json()

    # List jobs
    list_res = client.get("/api/v1/jobs", headers=headers)
    assert list_res.status_code == 200
    jobs = list_res.json()
    assert len(jobs) == 2

    # Get single job
    get_res = client.get(f"/api/v1/jobs/{j1['id']}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["company"] == "Company A"


def test_update_and_delete_job(client):
    """API test: update job metadata and delete job record."""
    token = get_user_token(client, "job_mod_user@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    job = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"company": "Old Corp", "title": "Engineer", "raw_jd_text": "Old JD"},
    ).json()
    job_id = job["id"]

    # Update job
    up_res = client.put(
        f"/api/v1/jobs/{job_id}",
        headers=headers,
        json={"company": "New Corp", "status": "archived"},
    )
    assert up_res.status_code == 200
    assert up_res.json()["company"] == "New Corp"
    assert up_res.json()["status"] == "archived"

    # Delete job
    del_res = client.delete(f"/api/v1/jobs/{job_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify deleted
    assert client.get(f"/api/v1/jobs/{job_id}", headers=headers).status_code == 404


def test_jobs_user_isolation(client):
    """Security test: User 1 cannot view, update, or delete User 2's jobs."""
    token1 = get_user_token(client, "job_iso_1@test.local")
    token2 = get_user_token(client, "job_iso_2@test.local")
    h1 = {"Authorization": f"Bearer {token1}"}
    h2 = {"Authorization": f"Bearer {token2}"}

    job1 = client.post(
        "/api/v1/jobs",
        headers=h1,
        json={"company": "Confidential Startup", "title": "Lead", "raw_jd_text": "Private JD"},
    ).json()
    job1_id = job1["id"]

    # User 2 cannot get User 1's job
    assert client.get(f"/api/v1/jobs/{job1_id}", headers=h2).status_code == 404

    # User 2 cannot update User 1's job
    assert client.put(
        f"/api/v1/jobs/{job1_id}",
        headers=h2,
        json={"company": "Hacked"},
    ).status_code == 404

    # User 2 cannot delete User 1's job
    assert client.delete(f"/api/v1/jobs/{job1_id}", headers=h2).status_code == 404

    # User 2's jobs list must not show User 1's job
    u2_jobs = client.get("/api/v1/jobs", headers=h2).json()
    assert len(u2_jobs) == 0
