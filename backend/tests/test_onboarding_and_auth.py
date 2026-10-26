import pytest
from fastapi.testclient import TestClient


def test_user_onboarding_lifecycle(client: TestClient):
    # 1. Register new user
    email = "new_onboarding_user@example.com"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!", "full_name": "New User"},
    )
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["onboarding_completed"] is False

    # 2. Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Read profile before completing onboarding
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["onboarding_completed"] is False

    # 4. Explicitly complete onboarding (e.g. skip or finish guide)
    onboard_res = client.post("/api/v1/auth/onboarding/complete", headers=headers)
    assert onboard_res.status_code == 200
    assert onboard_res.json()["onboarding_completed"] is True

    # 5. Verify /auth/me reflects completed onboarding
    me_res2 = client.get("/api/v1/auth/me", headers=headers)
    assert me_res2.status_code == 200
    assert me_res2.json()["onboarding_completed"] is True
