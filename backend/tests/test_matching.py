import pytest


def get_auth_token(client, email="match_candidate@test.local"):
    """Helper to authenticate a test user and obtain bearer token."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password12345", "full_name": "Match Candidate"},
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password12345"},
    )
    return res.json()["access_token"]


def test_match_job_and_retrieve(client):
    """API test: create job, analyze, and compute deterministic match analysis."""
    token = get_auth_token(client, "candidate_match_1@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Setup candidate profile with skills and a project
    client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"name": "Python", "category": "Language", "proficiency": "Advanced"},
    )
    client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"name": "FastAPI", "category": "Framework", "proficiency": "Intermediate"},
    )
    client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"name": "GraphQL", "category": "Language", "proficiency": "Expert"},  # Expert but no project -> Unsupported claim
    )
    client.post(
        "/api/v1/profile/projects",
        headers=headers,
        json={
            "title": "API Backend Engine",
            "role": "Lead",
            "technologies": ["Python", "FastAPI"],
            "bullets": ["Engineered high-throughput endpoints"],
        },
    )

    # 2. Create target job requiring Python, FastAPI, and Kubernetes
    job = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "company": "ScaleWorks",
            "title": "Senior Python Architect",
            "raw_jd_text": (
                "Requirements:\n"
                "- Strong proficiency in Python and FastAPI\n"
                "- Experience with Kubernetes and Docker\n"
                "- Bonus: PostgreSQL and Redis\n"
            ),
        },
    ).json()
    job_id = job["id"]

    # 3. Analyze JD
    client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)

    # 4. Trigger match analysis
    match_res = client.post(f"/api/v1/jobs/{job_id}/match", headers=headers)
    assert match_res.status_code == 200
    data = match_res.json()
    assert data["job_id"] == job_id
    assert 0 <= data["estimated_match_score"] <= 100

    # Matched skills should contain Python and FastAPI because they exist in profile AND project
    assert "Python" in data["matched_skills"]
    assert "FastAPI" in data["matched_skills"]

    # Kubernetes is required by JD but not in candidate profile -> Missing skills
    assert "Kubernetes" in data["missing_skills"]

    # GraphQL is claimed as Expert with 0 projects -> Unsupported claim
    assert any("GraphQL" in claim for claim in data["unsupported_claims"])

    # Evidence map should link Python and FastAPI to the project
    assert "Python" in data["evidence_map"]
    assert any("API Backend Engine" in src for src in data["evidence_map"]["Python"])

    # 5. Retrieve existing match via GET
    get_res = client.get(f"/api/v1/jobs/{job_id}/match", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["estimated_match_score"] == data["estimated_match_score"]


def test_match_unauthorized_isolation(client):
    """Security test: User 1 match cannot be accessed or triggered by User 2."""
    t1 = get_auth_token(client, "user_match_iso1@test.local")
    t2 = get_auth_token(client, "user_match_iso2@test.local")
    h1 = {"Authorization": f"Bearer {t1}"}
    h2 = {"Authorization": f"Bearer {t2}"}

    job = client.post(
        "/api/v1/jobs",
        headers=h1,
        json={"company": "Secure AI", "title": "Dev", "raw_jd_text": "Python required"},
    ).json()
    job_id = job["id"]
    client.post(f"/api/v1/jobs/{job_id}/analyze", headers=h1)
    client.post(f"/api/v1/jobs/{job_id}/match", headers=h1)

    # User 2 attempts to get User 1's match -> 404
    assert client.get(f"/api/v1/jobs/{job_id}/match", headers=h2).status_code == 404
