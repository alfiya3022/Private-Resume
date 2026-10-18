import pytest
from fastapi.testclient import TestClient


def setup_candidate_job_and_resume(client: TestClient, email: str, name: str):
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
        json={"headline": "Software Engineer", "phone": "555-0100", "location": "Remote"},
        headers=headers,
    )

    client.post(
        "/api/v1/profile/skills",
        json={"name": "Go", "category": "Language", "proficiency": "Expert"},
        headers=headers,
    )

    job_res = client.post(
        "/api/v1/jobs",
        json={
            "company": "CloudScale",
            "title": "Backend Systems Engineer",
            "raw_jd_text": "Golang, Kubernetes, distributed systems.",
        },
        headers=headers,
    )
    job_id = job_res.json()["id"]

    tailor_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = tailor_res.json()["id"]

    return headers, job_id, resume_id


def test_create_and_list_applications(client: TestClient):
    headers, job_id, resume_id = setup_candidate_job_and_resume(
        client, "app_user1@test.local", "App Candidate 1"
    )

    # 1. Create application
    payload = {
        "job_id": job_id,
        "tailored_resume_id": resume_id,
        "status": "applied",
        "notes": "Submitted application via company career portal with v1 PDF.",
    }
    res = client.post("/api/v1/applications", json=payload, headers=headers)
    assert res.status_code == 201
    app_data = res.json()
    assert app_data["job_id"] == job_id
    assert app_data["tailored_resume_id"] == resume_id
    assert app_data["status"] == "applied"
    assert "portal" in app_data["notes"]
    app_id = app_data["id"]

    # 2. List applications
    list_res = client.get("/api/v1/applications", headers=headers)
    assert list_res.status_code == 200
    apps = list_res.json()
    assert len(apps) >= 1
    found = next((a for a in apps if a["id"] == app_id), None)
    assert found is not None
    assert found["job"]["company"] == "CloudScale"
    assert found["tailored_resume"]["version_number"] == 1

    # 3. Get single application
    single_res = client.get(f"/api/v1/applications/{app_id}", headers=headers)
    assert single_res.status_code == 200
    assert single_res.json()["id"] == app_id


def test_filter_and_update_application_status(client: TestClient):
    headers, job_id, resume_id = setup_candidate_job_and_resume(
        client, "app_user2@test.local", "App Candidate 2"
    )

    create_res = client.post(
        "/api/v1/applications",
        json={"job_id": job_id, "tailored_resume_id": resume_id, "status": "applied"},
        headers=headers,
    )
    app_id = create_res.json()["id"]

    # Update to 'interviewing'
    update_res = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "interviewing", "notes": "Recruiter phone screen scheduled for Thursday."},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "interviewing"
    assert "Thursday" in update_res.json()["notes"]

    # Filter by interviewing
    filter_res = client.get("/api/v1/applications?status=interviewing", headers=headers)
    assert filter_res.status_code == 200
    assert any(a["id"] == app_id for a in filter_res.json())

    # Filter by rejected should be empty
    empty_res = client.get("/api/v1/applications?status=rejected", headers=headers)
    assert empty_res.status_code == 200
    assert not any(a["id"] == app_id for a in empty_res.json())


def test_delete_application(client: TestClient):
    headers, job_id, resume_id = setup_candidate_job_and_resume(
        client, "app_user3@test.local", "App Candidate 3"
    )

    create_res = client.post(
        "/api/v1/applications",
        json={"job_id": job_id, "status": "draft"},
        headers=headers,
    )
    app_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/applications/{app_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify 404
    get_res = client.get(f"/api/v1/applications/{app_id}", headers=headers)
    assert get_res.status_code == 404


def test_application_user_isolation(client: TestClient):
    headers_a, job_id_a, resume_id_a = setup_candidate_job_and_resume(
        client, "app_user_a@test.local", "User A"
    )

    create_res = client.post(
        "/api/v1/applications",
        json={"job_id": job_id_a, "tailored_resume_id": resume_id_a, "status": "applied"},
        headers=headers_a,
    )
    app_id_a = create_res.json()["id"]

    # User B setup
    client.post(
        "/api/v1/auth/register",
        json={"email": "app_user_b@test.local", "password": "SecurePassword123!", "full_name": "User B"},
    )
    login_b = client.post(
        "/api/v1/auth/login",
        json={"email": "app_user_b@test.local", "password": "SecurePassword123!"},
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    # User B cannot view User A's application
    assert client.get(f"/api/v1/applications/{app_id_a}", headers=headers_b).status_code == 404

    # User B cannot update User A's application
    assert client.patch(
        f"/api/v1/applications/{app_id_a}",
        json={"status": "offer"},
        headers=headers_b,
    ).status_code == 404

    # User B cannot delete User A's application
    assert client.delete(f"/api/v1/applications/{app_id_a}", headers=headers_b).status_code == 404

    # User B cannot log an application for User A's job
    assert client.post(
        "/api/v1/applications",
        json={"job_id": job_id_a, "status": "applied"},
        headers=headers_b,
    ).status_code == 404
