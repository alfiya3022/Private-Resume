from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.profile import (
    CandidateProfile,
    CandidateSkill,
    Project,
    Experience,
    Education,
)
from app.models.job import Job

db = SessionLocal()

# Check if demo user exists
user = db.query(User).filter(User.email == "demo@privateresume.local").first()
if not user:
    user = User(
        email="demo@privateresume.local",
        hashed_password=get_password_hash("Password123!"),
        full_name="Alex Morgan",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created demo user: {user.email}")

# Candidate profile
profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
if not profile:
    profile = CandidateProfile(
        user_id=user.id,
        headline="Senior Backend Engineer",
        phone="+1 (555) 019-2834",
        location="San Francisco, CA",
        github_url="https://github.com/alexmorgan-dev",
        summary="Backend specialist with 5+ years of experience building high-throughput APIs in Python, FastAPI, and PostgreSQL.",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Skills
    skills = [
        ("Python", "Language", "Advanced"),
        ("FastAPI", "Framework", "Advanced"),
        ("PostgreSQL", "Database", "Advanced"),
        ("Docker", "Tool", "Intermediate"),
        ("Git", "Tool", "Advanced"),
        ("Linux", "Tool", "Intermediate"),
        ("Pytest", "Tool", "Advanced"),
    ]
    for name, cat, prof in skills:
        db.add(CandidateSkill(profile_id=profile.id, name=name, category=cat, proficiency=prof))

    # Experience
    exp1 = Experience(
        profile_id=profile.id,
        company="NovaTech Solutions",
        title="Senior Backend Engineer",
        location="San Francisco, CA",
        start_date="2022-03",
        end_date="Present",
        description="Architected low-latency REST APIs handling 40,000+ requests per second using FastAPI and PostgreSQL.\nReduced database query latency by 45% by introducing optimized composite indexing.\nContainerized 12 backend microservices with Docker and streamlined automated CI testing.",
        bullets=[
            "Architected low-latency REST APIs handling 40,000+ requests per second using FastAPI and PostgreSQL.",
            "Reduced database query latency by 45% by introducing optimized composite indexing.",
            "Containerized 12 backend microservices with Docker and streamlined automated CI testing.",
        ],
        is_current=True,
    )
    exp2 = Experience(
        profile_id=profile.id,
        company="DataPulse Inc",
        title="Software Engineer",
        location="San Jose, CA",
        start_date="2020-06",
        end_date="2022-02",
        description="Engineered Python data ingestion pipelines handling 5GB of daily telemetry data.\nAuthored comprehensive Pytest test suites achieving 92% integration coverage.",
        bullets=[
            "Engineered Python data ingestion pipelines handling 5GB of daily telemetry data.",
            "Authored comprehensive Pytest test suites achieving 92% integration coverage.",
        ],
        is_current=False,
    )
    db.add_all([exp1, exp2])

    # Projects
    p1 = Project(
        profile_id=profile.id,
        title="Distributed Task Engine",
        role="Lead Architect",
        description="Built distributed worker pool processing asynchronous jobs with guaranteed idempotency and telemetry.",
        bullets=[
            "Built distributed worker pool processing asynchronous jobs with guaranteed idempotency.",
            "Integrated real-time health telemetry and alerting reducing incident resolution time by 30%.",
        ],
        technologies=["Python", "FastAPI", "Docker", "PostgreSQL"],
        url="https://github.com/alexmorgan-dev/task-engine",
    )
    p2 = Project(
        profile_id=profile.id,
        title="Cloud Resume Compiler",
        role="Creator",
        description="Created isolated document generation pipeline executing LaTeX to PDF transformations safely.",
        bullets=[
            "Created isolated document generation pipeline executing LaTeX to PDF transformations safely.",
            "Implemented strict sanitization against LaTeX macro injection.",
        ],
        technologies=["Python", "LaTeX", "Docker"],
        url="https://github.com/alexmorgan-dev/resume-compiler",
    )
    db.add_all([p1, p2])

    # Education
    edu = Education(
        profile_id=profile.id,
        institution="University of California, Berkeley",
        degree="B.S. in Computer Science",
        field_of_study="Computer Science",
        grade="3.85 GPA",
        start_date="2016",
        end_date="2020",
    )
    db.add(edu)
    db.commit()
    print("Seeded candidate profile, skills, experiences, and projects!")

# Sample Job
job = db.query(Job).filter(Job.user_id == user.id).first()
if not job:
    job = Job(
        user_id=user.id,
        company="Stripe Platforms",
        title="Senior Python Backend Engineer",
        location="San Francisco, CA (Hybrid)",
        salary="$165,000 - $190,000",
        job_url="https://stripe.com/jobs/senior-python-engineer",
        raw_jd_text="""We are looking for a Senior Python Backend Engineer to join our Core Platform team.

Requirements:
• 4+ years of professional software engineering experience with Python.
• Strong expertise with FastAPI or modern async Python frameworks.
• Proficient with relational databases, specifically PostgreSQL.
• Hands-on experience with Docker and automated testing (Pytest).
• Bonus: Experience with Kubernetes or distributed systems.

Responsibilities:
• Design, develop, and maintain mission-critical payment APIs.
• Collaborate with infrastructure teams to ensure 99.99% uptime.
• Write clean, testable code and participate in architectural reviews.""",
        status="Saved",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    print(f"Seeded sample job: {job.title} at {job.company}")

db.close()
print("Seeding complete!")
