def test_root_endpoint(client):
    """Smoke test root entry endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "PrivateResume API"


def test_health_check_endpoint(client):
    """Smoke test API v1 health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "subsystems" in data
    assert "database" in data["subsystems"]
    assert "ollama" in data["subsystems"]
    assert "latex" in data["subsystems"]


def test_security_headers_present(client):
    """Verify security headers middleware attaches required protection headers."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "SAMEORIGIN"
    assert response.headers.get("x-xss-protection") == "1; mode=block"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

