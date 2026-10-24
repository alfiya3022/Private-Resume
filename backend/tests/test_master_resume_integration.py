import io
import fitz
import pytest
from app.models.profile import CandidateProfile, Project, Certification
from app.models.resume import MasterResume
from app.models.tailored_resume import TailoredResume
from app.services.pdf_service import pdf_service
from app.services.resolution_service import resolution_service


def create_rich_synthetic_resume_pdf() -> bytes:
    """Creates a synthetic multi-section PDF resume with clickable link annotations."""
    doc = fitz.open()
    page = doc.new_page()

    # Write text
    text_content = """Alfiya Shaikh
Email: alfiya.shaikh@example.com | Phone: +91 98765 43210
Location: Mumbai, India
GitHub | LinkedIn

SUMMARY
Full-Stack Software Engineer with 2+ years of experience in Python, FastAPI, and React.

TECHNICAL SKILLS
Python, JavaScript, TypeScript, FastAPI, React, PostgreSQL, Docker, Git

EXPERIENCE
Software Engineer
Tech Innovations Pvt Ltd (Mumbai, India)
Jan 2023 - Present
• Built high-performance async REST APIs using FastAPI and PostgreSQL.
• Containerized microservices using Docker and orchestrated CI/CD pipelines.

PROJECTS
Private Resume - AI Resume Tailor
Technologies: Python, FastAPI, React, PostgreSQL
• Local-first privacy-focused resume generator using deterministic extraction.
• Implemented LaTeX compilation and PyMuPDF text extraction.

EDUCATION
Bachelor of Engineering in Computer Science
Mumbai University
2019 - 2023
CGPA: 8.95

CERTIFICATIONS
AWS Certified Cloud Practitioner - Amazon Web Services - 2023
"""
    rect = fitz.Rect(50, 50, 550, 750)
    page.insert_textbox(rect, text_content, fontsize=10, fontname="helv")

    # Add link annotations for GitHub and LinkedIn
    gh_rect = fitz.Rect(50, 85, 100, 95)
    page.insert_link({
        "kind": fitz.LINK_URI,
        "from": gh_rect,
        "uri": "https://github.com/alfiyashaikh",
    })

    li_rect = fitz.Rect(110, 85, 160, 95)
    page.insert_link({
        "kind": fitz.LINK_URI,
        "from": li_rect,
        "uri": "https://linkedin.com/in/alfiyashaikh",
    })

    # Add project repo link
    proj_rect = fitz.Rect(50, 290, 250, 305)
    page.insert_link({
        "kind": fitz.LINK_URI,
        "from": proj_rect,
        "uri": "https://github.com/alfiyashaikh/privateresume",
    })

    # Add cert credential link
    cert_rect = fitz.Rect(50, 480, 350, 495)
    page.insert_link({
        "kind": fitz.LINK_URI,
        "from": cert_rect,
        "uri": "https://aws.amazon.com/verification/cred-12345",
    })

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def get_auth_token(client, email="mresume_test@test.local"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123", "full_name": "Alfiya Shaikh"},
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123"},
    )
    return res.json()["access_token"]


def test_pdf_service_extract_full_resume_data(tmp_path):
    """Verify PyMuPDF extraction engine extracts personal info, links, skills, and sections."""
    pdf_bytes = create_rich_synthetic_resume_pdf()
    pdf_file = tmp_path / "test_resume.pdf"
    pdf_file.write_bytes(pdf_bytes)

    extracted = pdf_service.extract_full_resume_data(str(pdf_file))

    assert extracted is not None
    assert extracted["personal_info"]["name"] == "Alfiya Shaikh"
    assert "alfiya.shaikh@example.com" in extracted["personal_info"]["email"]
    assert "98765" in extracted["personal_info"]["phone"]
    assert "https://github.com/alfiyashaikh" in extracted["personal_info"]["github_url"]
    assert "https://linkedin.com/in/alfiyashaikh" in extracted["personal_info"]["linkedin_url"]

    # Verify skills detected
    skills = extracted["skills"]
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "React" in skills

    # Verify projects extracted with github_url
    assert len(extracted["projects"]) >= 1
    p0 = extracted["projects"][0]
    assert "Private Resume" in p0["title"]
    assert "https://github.com/alfiyashaikh/privateresume" == p0["github_url"]

    # Verify education
    assert len(extracted["education"]) >= 1
    e0 = extracted["education"][0]
    assert "Computer Science" in e0["degree"]
    assert "8.95" in e0["grade"]

    # Verify certification with credential URL
    assert len(extracted["certifications"]) >= 1
    c0 = extracted["certifications"][0]
    assert "AWS" in c0["name"]
    assert "https://aws.amazon.com/verification/cred-12345" == c0["credential_url"]


def test_master_resume_upload_and_review_flow(client):
    """API test: upload PDF, check extracted_data and comparison, then selectively apply to profile."""
    token = get_auth_token(client, "review_flow@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    pdf_bytes = create_rich_synthetic_resume_pdf()
    files = {"file": ("alfiya_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

    upload_res = client.post("/api/v1/resumes", headers=headers, files=files)
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    resume_id = upload_data["resume_id"]

    assert upload_data["extracted_data"] is not None
    assert upload_data["comparison"] is not None
    assert upload_data["extracted_data"]["personal_info"]["name"] == "Alfiya Shaikh"

    # 1. Fetch extracted data endpoint
    get_res = client.get(f"/api/v1/resumes/{resume_id}/extracted-data", headers=headers)
    assert get_res.status_code == 200
    ext_data = get_res.json()
    assert ext_data["resume_id"] == resume_id
    assert ext_data["extracted_data"]["personal_info"]["github_url"] == "https://github.com/alfiyashaikh"
    assert "personal_info" in ext_data["comparison"]

    # 2. Selectively apply personal_info and projects to profile
    apply_payload = {
        "sections": ["personal_info", "projects"],
        "overwrite_existing": False,
    }
    apply_res = client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json=apply_payload,
    )
    assert apply_res.status_code == 200
    applied_data = apply_res.json()
    assert applied_data["status"] == "success"
    assert applied_data["counts"]["projects_added"] >= 1

    # 3. Verify CandidateProfile updated with personal info and projects
    prof_res = client.get("/api/v1/profile", headers=headers)
    assert prof_res.status_code == 200
    prof = prof_res.json()
    assert prof["linkedin_url"] == "https://linkedin.com/in/alfiyashaikh"
    assert prof["github_url"] == "https://github.com/alfiyashaikh"
    assert len(prof["projects"]) >= 1
    assert prof["projects"][0]["title"] == "Private Resume - AI Resume Tailor"


def test_apply_extracted_data_agency_no_silent_overwrite(client):
    """Candidate agency: existing reviewed fields must NOT be overwritten when overwrite_existing=False."""
    token = get_auth_token(client, "agency_test@test.local")
    headers = {"Authorization": f"Bearer {token}"}

    # Set up user's profile with custom phone and custom LinkedIn
    client.put(
        "/api/v1/profile",
        headers=headers,
        json={
            "phone": "+91 99999 11111",
            "linkedin_url": "https://linkedin.com/in/custom-reviewed-profile",
        },
    )

    pdf_bytes = create_rich_synthetic_resume_pdf()
    files = {"file": ("agency_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/resumes", headers=headers, files=files)
    resume_id = upload_res.json()["resume_id"]

    # Apply with overwrite_existing=False
    client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json={"sections": ["personal_info"], "overwrite_existing": False},
    )

    # Check profile - custom reviewed phone and linkedin must be retained
    prof1 = client.get("/api/v1/profile", headers=headers).json()
    assert prof1["phone"] == "+91 99999 11111"
    assert prof1["linkedin_url"] == "https://linkedin.com/in/custom-reviewed-profile"
    # Empty field (github_url) was safely populated from extraction
    assert prof1["github_url"] == "https://github.com/alfiyashaikh"

    # Now apply with overwrite_existing=True
    client.post(
        f"/api/v1/resumes/{resume_id}/apply-to-profile",
        headers=headers,
        json={"sections": ["personal_info"], "overwrite_existing": True},
    )

    prof2 = client.get("/api/v1/profile", headers=headers).json()
    assert "98765" in prof2["phone"]
    assert prof2["linkedin_url"] == "https://linkedin.com/in/alfiyashaikh"


def test_pre_generation_resolution_precedence(db_session):
    """Tests ResolutionService source precedence: Tailored Resume > Profile > Master Resume > None."""
    from app.models.user import User

    test_user = User(
        email="resolution_prec@test.local",
        hashed_password="hashed_pw_placeholder",
        full_name="Alfiya Shaikh",
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # 1. Setup profile with phone and linkedin
    profile = CandidateProfile(
        user_id=test_user.id,
        phone="+91 11111 22222",
        linkedin_url="https://linkedin.com/in/profile-linkedin",
        github_url=None,  # missing on profile
    )
    db_session.add(profile)

    # 2. Setup master resume with extracted github and project
    master = MasterResume(
        user_id=test_user.id,
        filename="master.pdf",
        file_path="/tmp/fake.pdf",
        file_size=1024,
        raw_text="...",
        extracted_data={
            "personal_info": {
                "phone": "+91 88888 77777",
                "linkedin_url": "https://linkedin.com/in/master-linkedin",
                "github_url": "https://github.com/master-github",
            },
            "projects": [
                {
                    "title": "Alpha Project",
                    "github_url": "https://github.com/master/alpha",
                    "dates": "2023",
                },
                {
                    "title": "Excluded Project Beta",
                    "github_url": "https://github.com/master/beta",
                },
            ],
            "certifications": [
                {
                    "name": "AWS Solutions Architect",
                    "credential_url": "https://aws.cert/master-cred",
                    "issuer": "AWS",
                }
            ],
        },
        is_active=True,
    )
    db_session.add(master)

    # 3. Setup tailored resume with:
    # - explicit custom location
    # - missing phone, missing linkedin, missing github in contact_info
    # - only Alpha Project (Excluded Project Beta was omitted by tailoring)
    # - AWS Solutions Architect certification missing credential_url
    tailored = TailoredResume(
        user_id=test_user.id,
        job_id=1,
        version_number=1,
        status="draft",
        content={
            "contact_info": {
                "location": "Bengaluru, India",
            },
            "projects": [
                {
                    "name": "Alpha Project",
                    "technologies": ["Python"],
                    "bullets": ["Implemented key features."],
                }
            ],
            "certifications": [
                {
                    "name": "AWS Solutions Architect",
                    "year": "2023",
                }
            ],
        },
    )
    db_session.add(tailored)
    db_session.commit()

    effective, provenance = resolution_service.resolve_effective_content(
        db=db_session, user=test_user, resume=tailored
    )

    # 1. Location came from tailored resume
    assert effective["contact_info"]["location"] == "Bengaluru, India"
    assert provenance["contact.location"] == "tailored_resume"

    # 2. LinkedIn recovered from Profile (precedence 2 over Master Resume)
    assert effective["contact_info"]["linkedin"] == "https://linkedin.com/in/profile-linkedin"
    assert provenance["contact.linkedin"] == "profile"

    # 3. Phone recovered from Profile
    assert effective["contact_info"]["phone"] == "+91 11111 22222"
    assert provenance["contact.phone"] == "profile"

    # 4. GitHub recovered from Master Resume (missing in Tailored and Profile)
    assert effective["contact_info"]["github"] == "https://github.com/master-github"
    assert provenance["contact.github"] == "master_resume"

    # 5. Project Alpha had github_url recovered from Master Resume
    assert effective["projects"][0]["github_url"] == "https://github.com/master/alpha"
    assert provenance["project.0.github_url"] == "master_resume"

    # 6. Certification credential_url recovered from Master Resume
    assert effective["certifications"][0]["certificate_url"] == "https://aws.cert/master-cred"
    assert provenance["certification.0.url"] == "master_resume"

    # 7. CRITICAL RULE: Excluded Project Beta was NOT restored!
    assert len(effective["projects"]) == 1
    assert effective["projects"][0]["name"] == "Alpha Project"

    # 8. CRITICAL RULE: Database record of tailored resume was NOT mutated!
    db_session.refresh(tailored)
    assert "github_url" not in tailored.content["projects"][0]
    assert "linkedin" not in (tailored.content.get("contact_info") or {})


def test_multi_role_and_wrapped_bullet_experience_extraction():
    """Verify deterministic parser captures multi-role at same company and wrapped bullet continuation."""
    raw_exp = """Senior Software Engineer | Jan 2023 - Present
Google | Mountain View, CA
• Architected scalable distributed event-driven messaging service handling 10k req/sec
  with 99.99% uptime and zero packet loss across multi-region deployment.
• Spearheaded team migration to FastAPI microservices.

Software Engineer | Jun 2021 - Dec 2022
• Developed core search indexing algorithms and database optimization pipelines.
  Achieved 35% reduction in query latency and improved cache hit ratio.
"""
    exps = pdf_service._extract_experience(raw_exp)
    assert len(exps) == 2

    # First role
    r0 = exps[0]
    assert r0["title"] == "Senior Software Engineer"
    assert "Google" in r0["company"]
    assert r0["is_current"] is True
    assert len(r0["bullets"]) == 2
    # Check that wrapped bullet was concatenated properly
    assert "with 99.99% uptime" in r0["bullets"][0]

    # Second role (inherited company Google from previous role)
    r1 = exps[1]
    assert r1["title"] == "Software Engineer"
    assert "Google" in r1["company"]
    assert r1["is_current"] is False
    assert len(r1["bullets"]) == 1
    assert "Achieved 35% reduction" in r1["bullets"][0]


def test_project_extraction_with_technologies_dates_and_isolated_links():
    """Verify separate project records, technology extraction, dates, and strict single-link assignment."""
    raw_proj = """Alpha Search Engine (Python, FastAPI, Redis) | Jan 2023 - May 2023
• High-performance semantic search platform with vector embeddings.
  Integrated full-text caching and automated regression testing.

Beta Analytics Dashboard [React, Tailwind CSS, TypeScript] | Aug 2023 - Nov 2023
• Interactive telemetry dashboard for real-time cluster health monitoring.
"""
    links = [
        {"uri": "https://github.com/candidate/alpha-search-engine"},
        {"uri": "https://beta-dashboard.vercel.app"},
    ]

    projs = pdf_service._extract_projects(raw_proj, links=links)
    assert len(projs) == 2

    # Project 1
    p0 = projs[0]
    assert "Alpha Search Engine" in p0["title"]
    assert "Python" in p0["technologies"]
    assert "FastAPI" in p0["technologies"]
    assert p0["github_url"] == "https://github.com/candidate/alpha-search-engine"
    assert p0["live_url"] == ""  # Did NOT leak Beta's live URL!
    assert "Integrated full-text caching" in p0["bullets"][0]

    # Project 2
    p1 = projs[1]
    assert "Beta Analytics Dashboard" in p1["title"]
    assert "React" in p1["technologies"]
    assert p1["live_url"] == "https://beta-dashboard.vercel.app"
    assert p1["github_url"] == ""  # Did NOT leak Alpha's github URL!


def test_certification_extraction_details():
    """Verify extraction of issuer, credential ID, date, and URL."""
    raw_cert = """AWS Certified Solutions Architect - Amazon Web Services - 2023
Credential ID: AWS-SAA-987654
• Issued by AWS Training and Certification.
"""
    links = [
        {"uri": "https://aws.amazon.com/verify/AWS-SAA-987654"},
    ]

    certs = pdf_service._extract_certifications(raw_cert, links=links)
    assert len(certs) >= 1
    c0 = certs[0]
    assert "AWS Certified Solutions Architect" in c0["name"]
    assert "Amazon Web Services" in c0["issuer"] or "AWS" in c0["issuer"]
    assert c0["credential_id"] == "AWS-SAA-987654"
    assert c0["issue_date"] == "2023"
    assert c0["credential_url"] == "https://aws.amazon.com/verify/AWS-SAA-987654"


def test_source_grounding_validation():
    """Verify grounding validator rejects hallucinated companies, ungrounded bullets, and invented URLs."""
    source_text = "Software Engineer at Acme Corp from 2021 to 2023. Built authentication services with FastAPI."

    # 1. Experience grounding test
    untrusted_llm_exps = [
        {
            "company": "Acme Corp",
            "title": "Software Engineer",
            "bullets": [
                "Built authentication services with FastAPI.",
                "Invented artificial general intelligence and flew to Mars on a rocket.",  # Hallucination!
            ],
        },
        {
            "company": "Fictional Space Industries",  # Completely fabricated company!
            "title": "Chief Wizard",
            "bullets": ["Cast spells in production."],
        },
    ]

    grounded_exps = pdf_service.validate_and_ground_experience(untrusted_llm_exps, source_text)
    assert len(grounded_exps) == 1
    assert grounded_exps[0]["company"] == "Acme Corp"
    assert len(grounded_exps[0]["bullets"]) == 1
    assert "FastAPI" in grounded_exps[0]["bullets"][0]

    # 2. Project grounding & URL test
    project_source = "Personal project: MicroTask. A task manager built with Python and SQLite."
    doc_links = ["https://github.com/user/microtask"]

    untrusted_llm_projs = [
        {
            "title": "MicroTask",
            "technologies": ["Python", "SQLite"],
            "github_url": "https://github.com/fake-account/fake-repo",  # Fake URL not in doc_links or text!
            "live_url": "",
            "bullets": ["Task manager built with Python and SQLite."],
        }
    ]
    grounded_projs = pdf_service.validate_and_ground_projects(untrusted_llm_projs, project_source, doc_links)
    assert len(grounded_projs) == 1
    assert grounded_projs[0]["github_url"] == ""  # Hallucinated URL stripped!


@pytest.mark.asyncio
async def test_hybrid_extraction_fallback_when_ollama_unavailable(tmp_path):
    """Verify hybrid extraction falls back safely to deterministic baseline when Ollama is offline."""
    pdf_bytes = create_rich_synthetic_resume_pdf()
    pdf_file = tmp_path / "synthetic_resume.pdf"
    pdf_file.write_bytes(pdf_bytes)

    # Even if Ollama is not running, extract_full_resume_data_hybrid must succeed without exception
    result = await pdf_service.extract_full_resume_data_hybrid(str(pdf_file))
    assert result is not None
    assert result["personal_info"]["name"] == "Alfiya Shaikh"
    assert len(result["experience"]) >= 1
    assert len(result["projects"]) >= 1
    assert len(result["certifications"]) >= 1


def test_extract_projects_from_swe2_pdf_fixture():
    """Verify real-world fixture SWE(2).pdf extracts 3 separate projects with exact titles, dates, tech, and links."""
    import os
    fixture_path = "/app/tests/fixtures/SWE(2).pdf"
    if not os.path.exists(fixture_path):
        # Fallback to local path if running outside Docker
        fixture_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures", "SWE(2).pdf"))
    if not os.path.exists(fixture_path):
        pytest.skip("SWE(2).pdf fixture not found")

    data = pdf_service.extract_full_resume_data(fixture_path)
    projs = data.get("projects", [])
    assert len(projs) == 3

    # Project 1: First Home Fintech Solutions
    p0 = projs[0]
    assert "First Home Fintech Solutions — Full-Stack Web Application" in p0["title"]
    assert "Live" not in p0["technologies"]
    assert "React" in p0["technologies"]
    assert "FastAPI" in p0["technologies"]
    assert "Docker" in p0["technologies"]
    assert p0["start_date"] == "2026"
    assert p0["end_date"] == "Present"
    assert p0["live_url"] == "https://firsthomefintech.ae"
    assert p0["github_url"] == ""
    assert len(p0["bullets"]) == 2
    assert "lead management" in p0["bullets"][0]
    assert "encrypted database backups" in p0["bullets"][1]

    # Project 2: Private Resume
    p1 = projs[1]
    assert "Private Resume — AI-Powered Resume Application" in p1["title"]
    assert "FastAPI" in p1["technologies"]
    assert "SQLAlchemy" in p1["technologies"]
    assert "Ollama" in p1["technologies"]
    assert p1["end_date"] == "Oct 2026"
    assert p1["live_url"] == ""  # Did not leak p0's live URL
    assert len(p1["bullets"]) == 2
    assert "React frontend, FastAPI backend" in p1["bullets"][0]
    assert "JWT authentication" in p1["bullets"][1]

    # Project 3: Deep Learning-Based Image Fusion
    p2 = projs[2]
    assert "Deep Learning-Based Image Fusion" in p2["title"]
    assert "Python" in p2["technologies"]
    assert "PyTorch" in p2["technologies"]
    assert p2["start_date"] == "2025"
    assert p2["end_date"] == "2026"
    assert len(p2["bullets"]) == 2
    assert "model-training workflows" in p2["bullets"][0]
    assert "500 images" in p2["bullets"][1]


def test_extract_projects_multiline_and_badge_resilience():
    """Verify general-purpose resilience to multiline headers, badges, 'to' date ranges, and isolated links."""
    raw_proj = """Cloud Native Observability Platform [Live] [Code]
2023 to Present
Go, Kubernetes, Prometheus, Grafana
• Engineered automated telemetry pipeline aggregating logs from 50 microservices.
• Reduced mean-time-to-detection by 45% using proactive alert thresholds.

Edge Device Inference Engine (Demo)
Jan 2024 - Apr 2024
C++, TensorRT, OpenCV
• Implemented quantized model execution on resource-constrained hardware.
• Benchmarked inference throughput achieving 120 FPS.
"""
    links = [
        {"uri": "https://github.com/candidate/observability-code"},
        {"uri": "https://observability-live.io"},
        {"uri": "https://edge-demo.org"},
    ]

    projs = pdf_service._extract_projects(raw_proj, links=links)
    assert len(projs) == 2

    # Project 1: Cloud Native Observability Platform
    p0 = projs[0]
    assert p0["title"] == "Cloud Native Observability Platform"
    assert "Live" not in p0["technologies"]
    assert "Code" not in p0["technologies"]
    assert "Go" in p0["technologies"]
    assert "Kubernetes" in p0["technologies"]
    assert p0["start_date"] == "2023"
    assert p0["end_date"] == "Present"  # Not "Presen"
    assert p0["github_url"] == "https://github.com/candidate/observability-code"
    assert p0["live_url"] == "https://observability-live.io"
    assert len(p0["bullets"]) == 2

    # Project 2: Edge Device Inference Engine
    p1 = projs[1]
    assert p1["title"] == "Edge Device Inference Engine"
    assert "Demo" not in p1["technologies"]
    assert "C++" in p1["technologies"]
    assert "TensorRT" in p1["technologies"]
    assert p1["start_date"] == "Jan 2024"
    assert p1["end_date"] == "Apr 2024"
    assert p1["live_url"] == "https://edge-demo.org"
    assert p1["github_url"] == ""  # Did not leak p0's github URL
    assert len(p1["bullets"]) == 2


