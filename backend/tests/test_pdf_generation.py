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


def test_pdf_endpoint_auth_and_security(client: TestClient, db_session):
    headers = get_auth_token(client, "pdf_sec_user@test.local", "PDF Sec User")
    token = headers["Authorization"].split(" ")[1]

    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "Secure Co", "title": "SecEng", "raw_jd_text": "Python and security"},
        headers=headers,
    )
    job_id = job_res.json()["id"]
    resume_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = resume_res.json()["id"]

    pdf_gen_res = client.post(f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=headers)
    assert pdf_gen_res.status_code == 200

    # Case 1: Valid active user requesting their own PDF -> 200
    res_valid = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf", headers=headers)
    assert res_valid.status_code == 200
    assert res_valid.headers["content-type"] == "application/pdf"

    # Case 2: Missing Bearer token -> 401
    res_no_auth = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf")
    assert res_no_auth.status_code == 401

    # Case 3: Invalid Bearer token -> 401
    res_bad_token = client.get(
        f"/api/v1/tailored-resumes/{resume_id}/pdf",
        headers={"Authorization": "Bearer invalid_garbage_token"},
    )
    assert res_bad_token.status_code == 401

    # Case 4: Query-string JWT is NOT accepted as authentication substitute -> 401
    res_query_token = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf?token={token}")
    assert res_query_token.status_code == 401

    # Case 5: Nonexistent resume ID -> 404
    res_not_found = client.get("/api/v1/tailored-resumes/999999/pdf", headers=headers)
    assert res_not_found.status_code == 404

    # Case 6: Inactive user -> 400 (per project's get_current_user policy)
    from app.models.user import User
    user = db_session.query(User).filter(User.email == "pdf_sec_user@test.local").first()
    assert user is not None
    user.is_active = False
    db_session.commit()

    res_inactive = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf", headers=headers)
    assert res_inactive.status_code == 400
    assert "Inactive user account" in res_inactive.json().get("detail", "")


def test_pdf_generation_falls_back_when_custom_template_fails_compilation(client: TestClient):
    headers = get_auth_token(client, "broken_tpl_user@test.local", "Broken Template User")

    # 1. Upload a custom template that fails pdflatex compilation
    broken_tex = rb"\documentclass{article}\usepackage{nonexistentpackage123}\begin{document}Broken\end{document}"
    upload_res = client.post(
        "/api/v1/profile/template",
        headers=headers,
        files={"file": ("broken_template.tex", broken_tex, "application/x-tex")},
    )
    assert upload_res.status_code == 200

    # 2. Create job and tailored resume
    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "Fallback Corp", "title": "Lead Dev", "raw_jd_text": "Python and reliability."},
        headers=headers,
    )
    job_id = job_res.json()["id"]
    resume_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = resume_res.json()["id"]

    # 3. Generate PDF - must fall back gracefully to default ATS template and succeed with 200 instead of 500
    pdf_res = client.post(f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=headers)
    assert pdf_res.status_code == 200
    pdf_data = pdf_res.json()
    assert pdf_data["status"] == "success"
    assert pdf_data["pdf_artifact"]["file_size"] > 0

    # 4. Stream PDF endpoint must also succeed
    stream_res = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf", headers=headers)
    assert stream_res.status_code == 200
    assert stream_res.headers["content-type"] == "application/pdf"
    assert len(stream_res.content) > 1000

def test_pdf_generation_applies_rsection_custom_template(client: TestClient):
    headers = get_auth_token(client, "custom_rsec_user@test.local", "Custom RSec Candidate")

    # 1. Custom template using self-contained definition with rSection environments
    custom_tex = rb"""\documentclass{article}
\newenvironment{rSection}[1]{\section*{#1}}{}
\newcommand{\name}[1]{\def\candidatename{#1}}
\name{Old Dummy Name}
\begin{document}
\candidatename
\begin{rSection}{SUMMARY}
Old dummy summary
\end{rSection}
\begin{rSection}{SKILLS}
Old dummy skills
\end{rSection}
\begin{rSection}{EXPERIENCE}
Old dummy experience
\end{rSection}
\begin{rSection}{PROJECTS}
Old dummy projects
\end{rSection}
\begin{rSection}{EDUCATION}
Old dummy education
\end{rSection}
\begin{rSection}{Leadership}
Old sample leadership
\end{rSection}
\end{document}
"""

    upload_res = client.post(
        "/api/v1/profile/template",
        headers=headers,
        files={"file": ("custom_resume.tex", custom_tex, "application/x-tex")},
    )
    assert upload_res.status_code == 200

    # 2. Create job and tailor resume
    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "Custom Template Corp", "title": "Senior Data Architect", "raw_jd_text": "Python SQL cloud."},
        headers=headers,
    )
    job_id = job_res.json()["id"]
    resume_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = resume_res.json()["id"]

    # 3. Generate PDF - must use the custom template, not fall back to default
    pdf_res = client.post(f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=headers)
    assert pdf_res.status_code == 200
    pdf_data = pdf_res.json()
    assert pdf_data["status"] == "success"

    # 4. Verify TeX artifact reflects the custom template layout and candidate data
    tex_res = client.get(f"/api/v1/tailored-resumes/{resume_id}/tex", headers=headers)
    assert tex_res.status_code == 200
    tex_content = tex_res.text

    assert r"\begin{rSection}{SUMMARY}" in tex_content
    assert "Custom RSec Candidate" in tex_content
    assert "Old dummy summary" not in tex_content
    assert "Old dummy experience" not in tex_content
    # Sample sections not in resume data must be removed
    assert "Old sample leadership" not in tex_content

    # 5. Verify PDF artifact compiles and streams successfully
    stream_res = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf", headers=headers)
    assert stream_res.status_code == 200
    assert stream_res.headers["content-type"] == "application/pdf"
    assert stream_res.content.startswith(b"%PDF-")


def test_project_dates_and_certificate_links_rendering(client: TestClient):
    """Verifies project dates right-alignment, ongoing status, and certificate links."""
    headers = get_auth_token(client, "projectdates@example.com", "Project Test Candidate")

    # 1. Create job and tailored resume
    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "DateCorp", "title": "Lead Engineer", "raw_jd_text": "Python FastAPI PostgreSQL"},
        headers=headers,
    )
    job_id = job_res.json()["id"]
    resume_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = resume_res.json()["id"]

    # 2. Update resume with project dates, ongoing flag, and certificate links
    update_payload = {
        "content": {
            "summary": "Experienced engineer.",
            "skills": {"Languages": ["Python", "SQL"]},
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "Tech Solutions",
                    "location": "Remote",
                    "start_date": "2023",
                    "end_date": "Present",
                    "is_current": True,
                    "bullets": ["Led development team."],
                }
            ],
            "projects": [
                {
                    "name": "E-Commerce Engine",
                    "technologies": ["Python", "FastAPI"],
                    "start_date": "2024",
                    "end_date": "Present",
                    "is_current": True,
                    "live_url": "https://myecommerce.com",
                    "bullets": ["Engineered order processing."],
                },
                {
                    "name": "Legacy Analyzer",
                    "technologies": ["SQL"],
                    "start_date": "2022",
                    "end_date": "2023",
                    "github_url": "https://github.com/example/analyzer",
                    "bullets": ["Analyzed query performance."],
                },
                {
                    "name": "Undated Project",
                    "technologies": ["Docker"],
                    "bullets": ["Built containers."],
                },
            ],
            "education": [
                {
                    "institution": "State University",
                    "degree": "B.S. in Computer Science",
                    "year": "2018--2022",
                    "gpa": "3.9",
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Architect",
                    "issuer": "Amazon Web Services",
                    "certificate_url": "https://aws.amazon.com/verify/cert123",
                    "year": "2024",
                },
                {
                    "name": "Internal Hackathon Winner",
                    "issuer": "Tech Solutions",
                    "certificate_url": "",
                },
            ],
        },
        "save_as_new_version": False,
    }

    put_res = client.put(f"/api/v1/tailored-resumes/{resume_id}", json=update_payload, headers=headers)
    assert put_res.status_code == 200
    updated_resume = put_res.json()
    assert updated_resume["content"]["projects"][0]["start_date"] == "2024"
    assert updated_resume["content"]["projects"][0]["end_date"] == "Present"
    assert updated_resume["content"]["certifications"][0]["certificate_url"] == "https://aws.amazon.com/verify/cert123"

    # 3. Compile PDF
    gen_res = client.post(f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=headers)
    assert gen_res.status_code == 200
    assert gen_res.json()["status"] == "success"

    # 4. Check PDF stream and layout with PyMuPDF
    pdf_res = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")

    import fitz
    doc = fitz.open(stream=pdf_res.content, filetype="pdf")
    assert len(doc) == 1
    page = doc[0]
    extracted_text = page.get_text()

    # Experience dates right-aligned
    assert "2023–Present" in extracted_text or "2023" in extracted_text

    # Project dates rendered
    assert "2024–Present" in extracted_text or "2024" in extracted_text
    assert "2022–2023" in extracted_text

    # Undated project should not have dangling separators or undefined
    assert "undefined" not in extracted_text
    assert "null" not in extracted_text
    assert "Undated Project" in extracted_text

    # Certificate link and text in Certificate Name --- Provider --- Certificate format
    assert "AWS Certified Architect — Amazon Web Services — Certificate" in extracted_text
    # No certificate link label for hackathon winner
    assert "Internal Hackathon Winner — Tech Solutions" in extracted_text
    assert "[Certificate]" not in extracted_text

    # Verify real PDF link annotations
    uris = [l.get("uri") for l in page.get_links()]
    assert "https://myecommerce.com" in uris
    assert "https://github.com/example/analyzer" in uris
    assert "https://aws.amazon.com/verify/cert123" in uris


def test_linkedin_header_and_education_three_line_layout(client: TestClient):
    """Verifies LinkedIn under GitHub in header, 3-line Education layout, and Certificate link format."""
    headers = get_auth_token(client, "linkedinedu@example.com", "Alfiya Shaikh")

    # Set profile with LinkedIn and GitHub URLs
    client.put(
        "/api/v1/profile",
        json={
            "phone": "+91-8080713022",
            "location": "Mumbai, Maharashtra",
            "linkedin_url": "https://www.linkedin.com/in/alfiya-shaikh1106",
            "github_url": "https://github.com/alfiya3022",
            "headline": "Full-Stack Developer",
        },
        headers=headers,
    )

    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "Neuraleap", "title": "Developer", "raw_jd_text": "React FastAPI Python SQL"},
        headers=headers,
    )
    job_id = job_res.json()["id"]
    resume_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = resume_res.json()["id"]

    update_payload = {
        "content": {
            "summary": "Full-stack developer.",
            "skills": {"Languages": ["Python", "JavaScript"]},
            "education": [
                {
                    "degree": "B.E. Electronics & Telecommunication Engineering",
                    "institution": "Vidyavardhini’s College of Engineering",
                    "year": "2022--2026",
                    "gpa": "8.11",
                }
            ],
            "experience": [
                {
                    "title": "Freelance Developer",
                    "company": "First Home Fintech Solutions",
                    "start_date": "Jun 2026",
                    "end_date": "Present",
                    "bullets": ["Maintained production web app."],
                }
            ],
            "projects": [],
            "certifications": [
                {
                    "name": "The Complete SQL Bootcamp",
                    "issuer": "Udemy",
                    "certificate_url": "https://udemy.com/cert/sql123",
                },
                {
                    "name": "Patent Contributor",
                    "issuer": "Information Fusion",
                },
            ],
        },
        "save_as_new_version": False,
    }

    client.put(f"/api/v1/tailored-resumes/{resume_id}", json=update_payload, headers=headers)

    gen_res = client.post(f"/api/v1/tailored-resumes/{resume_id}/generate-pdf", headers=headers)
    assert gen_res.status_code == 200

    pdf_res = client.get(f"/api/v1/tailored-resumes/{resume_id}/pdf", headers=headers)
    assert pdf_res.status_code == 200

    import fitz
    doc = fitz.open(stream=pdf_res.content, filetype="pdf")
    page = doc[0]
    extracted = page.get_text()

    # 1. Header contains both GitHub and LinkedIn without raw URLs
    assert "GitHub" in extracted
    assert "LinkedIn" in extracted
    assert "linkedin.com" not in extracted
    assert "github.com" not in extracted

    # 2. Links check: LinkedIn is under GitHub in y coordinates
    links = page.get_links()
    gh_link = next(l for l in links if "github.com/alfiya3022" in l.get("uri", ""))
    li_link = next(l for l in links if "linkedin.com/in/alfiya-shaikh1106" in l.get("uri", ""))
    cert_link = next(l for l in links if "udemy.com/cert/sql123" in l.get("uri", ""))

    # LinkedIn Rect is vertically below GitHub Rect
    assert li_link["from"].y0 > gh_link["from"].y0

    # 3. Education separated onto 3 distinct lines
    lines = [line.strip() for line in extracted.splitlines() if line.strip()]
    edu_idx = lines.index("EDUCATION")
    assert "B.E. Electronics & Telecommunication Engineering" in lines[edu_idx + 1]
    assert "2022–2026" in lines[edu_idx + 2] or "2022--2026" in lines[edu_idx + 2]
    assert "Vidyavardhini’s College of Engineering" in lines[edu_idx + 3]
    assert "CGPA: 8.11" in lines[edu_idx + 4]

    # 4. Certifications formatted as Name --- Provider --- Certificate
    assert "The Complete SQL Bootcamp — Udemy — Certificate" in extracted
    assert "Patent Contributor — Information Fusion" in extracted

