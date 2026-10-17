import pytest
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token


def test_password_hashing():
    """Unit test: bcrypt password hashing and verification."""
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_token_encoding_decoding():
    """Unit test: JWT creation and payload decoding."""
    user_id = 42
    token = create_access_token(subject=user_id)
    assert isinstance(token, str)
    
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == str(user_id)


def test_register_user_success(client):
    """API test: successful candidate user registration."""
    payload = {
        "email": "candidate1@example.com",
        "password": "StrongPassword123",
        "full_name": "Jane Candidate",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "candidate1@example.com"
    assert data["full_name"] == "Jane Candidate"
    assert "id" in data
    assert data["is_active"] is True
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    """API negative test: prevent duplicate email registrations with 409 Conflict."""
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPassword123",
        "full_name": "First User",
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"].lower()


def test_register_invalid_email(client):
    """API validation test: reject malformed emails with 422."""
    payload = {
        "email": "not-an-email",
        "password": "StrongPassword123",
        "full_name": "Invalid User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_short_password(client):
    """API validation test: enforce minimum password length with 422."""
    payload = {
        "email": "short@example.com",
        "password": "short",
        "full_name": "Short Password",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client):
    """API test: authenticate valid credentials and receive JWT bearer token."""
    reg_payload = {
        "email": "login_user@example.com",
        "password": "ValidPassword999",
        "full_name": "Login User",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "email": "login_user@example.com",
        "password": "ValidPassword999",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """API negative test: reject bad password with 401."""
    reg_payload = {
        "email": "user_bad_pass@example.com",
        "password": "CorrectPassword123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user_bad_pass@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


def test_read_current_user_me(client):
    """API test: fetch current user via /me using bearer token."""
    reg_payload = {
        "email": "me_user@example.com",
        "password": "PasswordMe1234",
        "full_name": "Current Candidate",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "me_user@example.com", "password": "PasswordMe1234"},
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me_user@example.com"
    assert data["full_name"] == "Current Candidate"


def test_read_current_user_unauthorized(client):
    """Security test: reject unauthenticated request to protected /me endpoint."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_read_current_user_invalid_token(client):
    """Security test: reject forged or invalid token."""
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer forged.token.value"}
    )
    assert response.status_code == 401


def test_user_isolation(client):
    """Security test: user token cannot impersonate or access another user."""
    u1_reg = {
        "email": "user1@example.com",
        "password": "Password123456",
        "full_name": "User One",
    }
    u2_reg = {
        "email": "user2@example.com",
        "password": "Password123456",
        "full_name": "User Two",
    }
    client.post("/api/v1/auth/register", json=u1_reg)
    client.post("/api/v1/auth/register", json=u2_reg)

    t1_res = client.post(
        "/api/v1/auth/login",
        json={"email": "user1@example.com", "password": "Password123456"},
    )
    token1 = t1_res.json()["access_token"]

    # User 1 token must return User 1, not User 2
    me_res = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token1}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "user1@example.com"
    assert me_res.json()["email"] != "user2@example.com"
