import pytest
from fastapi.testclient import TestClient


def create_authenticated_user_with_profile(client: TestClient, email: str, name: str):
    # Register
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!", "full_name": name},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Setup profile
    client.put(
        "/api/v1/profile",
        json={"full_name": name, "title": "Staff Backend Engineer", "phone": "123-456-7890"},
        headers=headers,
    )

    # Add skills
    for skill in ["Python", "FastAPI", "PostgreSQL", "Docker"]:
        client.post(
            "/api/v1/profile/skills",
            json={"name": skill, "category": "technical", "proficiency": "expert"},
            headers=headers,
        )

    # Add project
    client.post(
        "/api/v1/profile/projects",
        json={
            "title": "Cloud Distributed Engine",
            "technologies": ["Python", "FastAPI", "Docker"],
            "description": "Architected low-latency microservices handling 50k requests per second.",
            "url": "https://github.com/candidate/engine",
        },
        headers=headers,
    )

    # Add experience
    client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Tech Corp",
            "title": "Senior Engineer",
            "location": "San Francisco, CA",
            "start_date": "2021-01",
            "end_date": "Present",
            "description": "Led backend engineering team in designing scalable APIs.",
        },
        headers=headers,
    )

    return headers


def test_tailor_resume_and_non_fabrication(client: TestClient):
    headers = create_authenticated_user_with_profile(client, "tailor_test@example.com", "Tailor Candidate")

    # Create job requiring Python, FastAPI, and missing skill Kubernetes
    job_res = client.post(
        "/api/v1/jobs",
        json={
            "company": "NextGen Platforms",
            "title": "Lead FastAPI Developer",
            "raw_jd_text": "We are seeking a Lead FastAPI Developer skilled in Python, FastAPI, and Kubernetes.",
        },
        headers=headers,
    )
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # Trigger JD analysis and match
    client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)
    client.post(f"/api/v1/jobs/{job_id}/match", headers=headers)

    # Tailor resume
    tailor_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    assert tailor_res.status_code == 201
    tailored = tailor_res.json()

    assert tailored["version_number"] == 1
    assert tailored["status"] == "draft"
    assert tailored["job_id"] == job_id
    assert "summary" in tailored["content"]
    assert "skills" in tailored["content"]
    assert "projects" in tailored["content"]
    assert "experience" in tailored["content"]

    # Verify Non-Fabrication Rule: Candidate's genuine skills are present, but missing 'Kubernetes' is NOT invented
    all_skills = []
    for cat, skl in tailored["content"]["skills"].items():
        all_skills.extend(skl)
    assert "Python" in all_skills
    assert "FastAPI" in all_skills
    assert "Kubernetes" not in all_skills  # Strictly preserved non-fabrication!


def test_tailored_resume_versioning_and_immutability(client: TestClient):
    headers = create_authenticated_user_with_profile(client, "version_test@example.com", "Version Candidate")

    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "ScaleAI", "title": "Senior Python Architect", "raw_jd_text": "Python and PostgreSQL required."},
        headers=headers,
    )
    job_id = job_res.json()["id"]

    # Create initial draft (v1)
    v1_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    assert v1_res.status_code == 201
    v1_id = v1_res.json()["id"]
    assert v1_res.json()["version_number"] == 1

    # In-place edit for v1 draft
    updated_content = v1_res.json()["content"]
    updated_content["summary"] = "Manually refined summary highlighting cloud scalability."
    put_res = client.put(
        f"/api/v1/tailored-resumes/{v1_id}",
        json={"content": updated_content, "save_as_new_version": False},
        headers=headers,
    )
    assert put_res.status_code == 200
    assert put_res.json()["id"] == v1_id
    assert put_res.json()["content"]["summary"] == "Manually refined summary highlighting cloud scalability."

    # Branch into v2
    v2_content = updated_content.copy()
    v2_content["summary"] = "Version 2 refined summary."
    v2_res = client.put(
        f"/api/v1/tailored-resumes/{v1_id}",
        json={"content": v2_content, "save_as_new_version": True},
        headers=headers,
    )
    assert v2_res.status_code == 200
    v2_id = v2_res.json()["id"]
    assert v2_res.json()["version_number"] == 2
    assert v2_res.json()["parent_version_id"] == v1_id
    assert v2_id != v1_id

    # Verify v1 is preserved and untouched (immutability)
    get_v1 = client.get(f"/api/v1/tailored-resumes/{v1_id}", headers=headers)
    assert get_v1.json()["content"]["summary"] == "Manually refined summary highlighting cloud scalability."

    # Finalize v2
    fin_res = client.post(f"/api/v1/tailored-resumes/{v2_id}/finalize", headers=headers)
    assert fin_res.status_code == 200
    assert fin_res.json()["status"] == "final"

    # Attempting to edit a finalized resume forces branching into a new version (v3) to protect historical immutability
    v3_content = v2_content.copy()
    v3_content["summary"] = "Version 3 summary after finalization."
    v3_res = client.put(
        f"/api/v1/tailored-resumes/{v2_id}",
        json={"content": v3_content, "save_as_new_version": False},
        headers=headers,
    )
    assert v3_res.status_code == 200
    assert v3_res.json()["version_number"] == 3
    assert v3_res.json()["status"] == "draft"

    # Check list of versions for job
    list_res = client.get(f"/api/v1/jobs/{job_id}/tailored-resumes", headers=headers)
    assert list_res.status_code == 200
    versions = list_res.json()
    assert len(versions) == 3
    assert [v["version_number"] for v in versions] == [1, 2, 3]


def test_ask_ai_section_editing(client: TestClient):
    headers = create_authenticated_user_with_profile(client, "ai_edit@example.com", "AI Edit Candidate")

    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "Innovate", "title": "Backend Lead", "raw_jd_text": "Backend engineering role."},
        headers=headers,
    )
    job_id = job_res.json()["id"]

    tailor_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = tailor_res.json()["id"]

    # Ask AI to refine experience bullets
    ai_res = client.post(
        f"/api/v1/tailored-resumes/{resume_id}/edit",
        json={
            "section": "experience",
            "instruction": "Transform into high-impact action bullets with active verbs.",
            "current_text": "Built web APIs and maintained system infrastructure.",
        },
        headers=headers,
    )
    assert ai_res.status_code == 200
    data = ai_res.json()
    assert data["section"] == "experience"
    assert len(data["suggested_text"]) > 10
    assert data["factuality_checked"] is True


def test_tailored_resume_security_isolation(client: TestClient):
    user1_headers = create_authenticated_user_with_profile(client, "user1_tailor@test.com", "User One")
    user2_headers = create_authenticated_user_with_profile(client, "user2_tailor@test.com", "User Two")

    # User 1 creates job and tailored resume
    job1_res = client.post(
        "/api/v1/jobs",
        json={"company": "User1 Co", "title": "Engineer", "raw_jd_text": "Python developer needed."},
        headers=user1_headers,
    )
    job1_id = job1_res.json()["id"]
    tailor1_res = client.post(f"/api/v1/jobs/{job1_id}/tailor", headers=user1_headers)
    resume1_id = tailor1_res.json()["id"]

    # User 2 attempts to get User 1's tailored resume -> 404
    assert client.get(f"/api/v1/tailored-resumes/{resume1_id}", headers=user2_headers).status_code == 404

    # User 2 attempts to tailor User 1's job -> 404
    assert client.post(f"/api/v1/jobs/{job1_id}/tailor", headers=user2_headers).status_code == 404

    # User 2 attempts to update User 1's resume -> 404
    assert client.put(
        f"/api/v1/tailored-resumes/{resume1_id}",
        json={"content": {}, "save_as_new_version": False},
        headers=user2_headers,
    ).status_code == 404
