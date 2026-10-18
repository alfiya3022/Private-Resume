"""
PrivateResume - Seed Data Script
Initializes a demo candidate user account with full profile, verified skills,
target job, tailored resume, and tracked application for quick onboarding and evaluation.
"""
from datetime import datetime, timezone
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.profile import (
    CandidateProfile,
    CandidateSkill,
    Experience,
    Education,
    Project,
)
from app.models.job import Job
from app.models.tailored_resume import TailoredResume
from app.models.application import Application


def seed():
    db = SessionLocal()
    try:
        # 1. Demo User
        demo_email = "demo@privateresume.local"
        existing = db.query(User).filter(User.email == demo_email).first()
        if existing:
            print(f"User '{demo_email}' already exists. Skipping user creation.")
            user = existing
        else:
            user = User(
                email=demo_email,
                hashed_password=get_password_hash("Password123!"),
                full_name="Alex Morgan",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo candidate: {user.email}")

        # 2. Candidate Master Profile
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        if not profile:
            profile = CandidateProfile(
                user_id=user.id,
                headline="Senior Distributed Systems Architect",
                summary="Staff Backend Engineer specializing in high-throughput transactional backends, microservice resilience, and PostgreSQL query optimization.",
                phone="555-019-2834",
                location="San Francisco, CA",
                linkedin_url="https://linkedin.com/in/alex-morgan-eng",
                github_url="https://github.com/alex-morgan-dev",
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            print("Created Candidate Master Profile.")

        # 3. Verified Skills
        core_skills = [
            ("Python", "Language", "Expert"),
            ("FastAPI", "Framework", "Expert"),
            ("PostgreSQL", "Database", "Expert"),
            ("Docker", "DevOps", "Advanced"),
            ("Kubernetes", "DevOps", "Intermediate"),
            ("Distributed Systems", "Architecture", "Expert"),
            ("Go", "Language", "Intermediate"),
            ("SQLAlchemy", "ORM", "Expert"),
            ("LaTeX", "Tools", "Advanced"),
        ]
        for name, category, proficiency in core_skills:
            if not db.query(CandidateSkill).filter(CandidateSkill.profile_id == profile.id, CandidateSkill.name == name).first():
                db.add(CandidateSkill(profile_id=profile.id, name=name, category=category, proficiency=proficiency))
        db.commit()

        # 4. Experience Record
        if not db.query(Experience).filter(Experience.profile_id == profile.id).first():
            db.add(
                Experience(
                    profile_id=profile.id,
                    company="CloudScale Systems",
                    title="Principal Backend Engineer",
                    location="San Francisco, CA",
                    start_date="2021",
                    end_date="Present",
                    description="Lead engineer for multi-region transactional payments infrastructure.",
                    bullets=[
                        "Architected distributed event streaming backend handling 50k transactions/sec with 99.99% SLA.",
                        "Optimized PostgreSQL connection pooling and indexing, cutting P99 database latency by 42%.",
                        "Containerized core microservices using Docker and deployed on Kubernetes with automated canary rollouts.",
                    ],
                )
            )
            db.commit()

        # 5. Education Record
        if not db.query(Education).filter(Education.profile_id == profile.id).first():
            db.add(
                Education(
                    profile_id=profile.id,
                    institution="University of California, Berkeley",
                    degree="B.S. in Computer Science",
                    field_of_study="Computer Systems & Software Engineering",
                    grade="3.85 GPA",
                )
            )
            db.commit()

        # 6. Target Job (Stripe)
        job = db.query(Job).filter(Job.user_id == user.id, Job.company == "Stripe").first()
        if not job:
            job = Job(
                user_id=user.id,
                company="Stripe",
                title="Staff Backend Engineer - Core Infrastructure",
                location="San Francisco, CA (Hybrid)",
                salary="$210,000 - $260,000",
                raw_jd_text="""We are looking for a Staff Backend Engineer to join our Core Infrastructure team.
Requirements:
- 7+ years building high-scale, resilient backend systems in Python, Go, or Java.
- Deep expertise in relational databases, transaction isolation, and PostgreSQL.
- Experience with Docker containerization, Kubernetes orchestration, and distributed tracing.
- Strong communication and architectural leadership.""",
                status="applied",
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            print("Created Target Opportunity (Stripe).")

        # 7. Pre-tailored Resume (v1)
        tailored = db.query(TailoredResume).filter(TailoredResume.user_id == user.id, TailoredResume.job_id == job.id).first()
        if not tailored:
            tailored = TailoredResume(
                user_id=user.id,
                job_id=job.id,
                version_number=1,
                status="final",
                target_role="Staff Backend Engineer - Core Infrastructure",
                content={
                    "headline": "Staff Backend Engineer - Core Infrastructure",
                    "summary": "Accomplished Backend Engineer with deep mastery of scalable Python services, PostgreSQL internals, and containerized cloud architectures.",
                    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Distributed Systems", "SQLAlchemy", "Kubernetes"],
                    "experience": [
                        {
                            "company": "CloudScale Systems",
                            "title": "Principal Backend Engineer",
                            "dates": "2021 -- Present",
                            "bullets": [
                                "Architected distributed event streaming backend handling 50k transactions/sec with 99.99% SLA.",
                                "Optimized PostgreSQL connection pooling and indexing, cutting P99 database latency by 42%.",
                                "Containerized core microservices using Docker with automated canary deployment pipelines.",
                            ],
                        }
                    ],
                    "education": [
                        {
                            "institution": "University of California, Berkeley",
                            "degree": "B.S. in Computer Science",
                            "year": "2020",
                        }
                    ],
                },
            )
            db.add(tailored)
            db.commit()
            db.refresh(tailored)
            print("Created Tailored Resume v1.")

        # 8. Tracked Application Record
        app_record = db.query(Application).filter(Application.user_id == user.id, Application.job_id == job.id).first()
        if not app_record:
            app_record = Application(
                user_id=user.id,
                job_id=job.id,
                tailored_resume_id=tailored.id,
                status="applied",
                notes="Submitted application via Stripe Career Portal. Resume snapshot locked to Tailored v1 with full ATS pre-flight validation.",
            )
            db.add(app_record)
            db.commit()
            print("Created Tracked Application Record.")

        print("\n[OK] Seed completed successfully!")
        print("Demo credentials: demo@privateresume.local / Password123!\n")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
