import os
import time
import pytest

def get_auth_token(client, email="test_apply_real@test.local"):
    """Helper to register and login a test user, returning bearer token."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123", "full_name": "Test Candidate"},
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123"},
    )
    return res.json()["access_token"]


REAL_TEMPLATES = [
    ("Alfiya_resume_DA.pdf", "Reference LaTeX"),
    ("Alfiya_Nvidia.pdf", "Single-page LaTeX"),
    ("DATA_Resume_temp1.pdf", "Sidebar/Multi-column"),
    ("DATA_Resume_temp4.pdf", "Symbol-delimited"),
    ("resume_DA.pdf", "Word Plain via Print-to-PDF"),
    ("resume template_2.pdf", "Icon-bullet Template"),
]


@pytest.mark.parametrize("pdf_name,label", REAL_TEMPLATES)
def test_apply_to_profile_succeeds_on_real_templates(client, pdf_name, label):
    """Verifies that full upload -> background extraction -> Apply to Profile completes

    with HTTP 200 and no timeouts on all 6 real templates, successfully populating candidate profile.
    """
    user_email = f"apply_{pdf_name.replace(' ', '_').replace('.', '_')}@test.local"
    token = get_auth_token(client, email=user_email)
    headers = {"Authorization": f"Bearer {token}"}

    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "fixtures", "heldout", "real")
    )
    pdf_path = os.path.join(base_dir, pdf_name)
    assert os.path.exists(pdf_path), f"Real fixture {pdf_path} not found"

    # Step 1: Upload resume PDF (runs background extraction task synchronously in TestClient)
    with open(pdf_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/resumes",
            headers=headers,
            files={"file": (pdf_name, f, "application/pdf")},
        )
    assert upload_res.status_code in (201, 202), f"Upload failed: {upload_res.status_code} {upload_res.text}"
    resume_id = upload_res.json()["resume_id"]

    # Step 2: Retrieve extracted data to verify extraction completed
    ext_res = client.get(f"/api/v1/resumes/{resume_id}/extracted-data", headers=headers)
    assert ext_res.status_code == 200
    ext_data = ext_res.json()["extracted_data"]
    assert ext_data is not None

    # Step 3: Apply to profile (overwrite_existing=False) and measure duration
    t0 = time.perf_counter()
    apply_payload = {
        "sections": ["personal_info", "skills", "projects", "experience", "education", "certifications"],
        "overwrite_existing": False,
        "edited_data": ext_data,
    }
    res = client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json=apply_payload,
    )
    duration = time.perf_counter() - t0

    assert res.status_code == 200, f"Apply failed with {res.status_code}: {res.text}"
    data = res.json()
    assert "counts" in data

    # Step 4: Verify candidate profile was populated
    prof_res = client.get("/api/v1/profile", headers=headers)
    assert prof_res.status_code == 200
    prof = prof_res.json()

    assert len(prof["skills"]) > 0, f"No skills populated for {pdf_name}"
    assert duration < 10.0, f"Apply took {duration:.2f}s, exceeding 10s budget"

    # Step 5: Test overwrite_existing = True
    res_overwrite = client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json={**apply_payload, "overwrite_existing": True},
    )
    assert res_overwrite.status_code == 200
