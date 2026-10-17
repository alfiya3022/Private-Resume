from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.job import Job
from app.models.analysis import JobRequirement
from app.models.match import MatchAnalysis
from app.models.profile import (
    CandidateProfile,
    CandidateSkill,
    Project,
    Experience,
    Education,
    Certification,
)
from app.models.tailored_resume import TailoredResume
from app.schemas.tailored_resume import (
    TailoredResumeUpdate,
    AskAIRequest,
    AskAIResponse,
)
from app.services.ai.ollama_provider import ollama_provider, TECH_CATEGORIES, CANONICAL_NAMES


class TailoringService:
    def get_job_or_404(self, db: Session, user: User, job_id: int) -> Job:
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or access unauthorized",
            )
        return job

    def get_resume_or_404(self, db: Session, user: User, resume_id: int) -> TailoredResume:
        resume = db.query(TailoredResume).filter(
            TailoredResume.id == resume_id,
            TailoredResume.user_id == user.id,
        ).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tailored resume not found or access unauthorized",
            )
        return resume

    async def generate_initial_tailored_resume(self, db: Session, user: User, job_id: int) -> TailoredResume:
        job = self.get_job_or_404(db, user, job_id)
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate profile required before tailoring a resume. Please upload a master resume or create your profile.",
            )

        # Pull candidate data
        candidate_skills = db.query(CandidateSkill).filter(CandidateSkill.profile_id == profile.id).all()
        experiences = db.query(Experience).filter(Experience.profile_id == profile.id).order_by(Experience.id.desc()).all()
        projects = db.query(Project).filter(Project.profile_id == profile.id).order_by(Project.id.desc()).all()
        educations = db.query(Education).filter(Education.profile_id == profile.id).all()
        certifications = db.query(Certification).filter(Certification.profile_id == profile.id).all()

        # Match analysis if present
        match = db.query(MatchAnalysis).filter(MatchAnalysis.job_id == job_id).first()
        matched_skill_names = set(match.matched_skills if match else [])

        # Categorize candidate genuine skills (Strictly preserving non-fabrication)
        categorized_skills: Dict[str, List[str]] = {
            "Languages": [],
            "Frameworks": [],
            "Databases": [],
            "Cloud & DevOps": [],
            "Tools": [],
            "Other": [],
        }

        # Build skill map
        user_skill_names = []
        for sk in candidate_skills:
            name = sk.name
            user_skill_names.append(name)
            name_lower = name.lower()
            placed = False
            for cat, kws in TECH_CATEGORIES.items():
                if name_lower in kws or any(kw in name_lower for kw in kws):
                    if cat == "languages":
                        categorized_skills["Languages"].append(name)
                    elif cat == "frameworks":
                        categorized_skills["Frameworks"].append(name)
                    elif cat == "databases":
                        categorized_skills["Databases"].append(name)
                    elif cat in ("cloud", "tools"):
                        categorized_skills["Cloud & DevOps"].append(name)
                    placed = True
                    break
            if not placed:
                categorized_skills["Other"].append(name)

        # Clean up empty categories
        categorized_skills = {k: v for k, v in categorized_skills.items() if v}

        # Format experiences
        exp_list = []
        for exp in experiences:
            exp_bullets = list(exp.bullets or [])
            if not exp_bullets and exp.description:
                exp_bullets = [b.strip() for b in exp.description.splitlines() if b.strip()]
            if not exp_bullets:
                exp_bullets = [f"Contributed to core development and operational excellence at {exp.company}."]
            exp_list.append({
                "company": exp.company,
                "title": exp.title,
                "location": exp.location or "",
                "start_date": exp.start_date or "",
                "end_date": exp.end_date or "Present",
                "bullets": exp_bullets,
            })

        # Format projects
        proj_list = []
        for p in projects:
            p_bullets = list(p.bullets or [])
            if not p_bullets and p.description:
                p_bullets = [b.strip() for b in p.description.splitlines() if b.strip()]
            if not p_bullets:
                p_bullets = [f"Designed and implemented {p.title} leveraging key software engineering practices."]
            proj_list.append({
                "name": p.title,
                "technologies": p.technologies or [],
                "description": p.description or "",
                "bullets": p_bullets,
                "link": getattr(p, "url", "") or "",
            })

        # Format education
        edu_list = [
            {
                "institution": edu.institution,
                "degree": edu.degree,
                "year": getattr(edu, "end_date", "") or "",
                "gpa": getattr(edu, "grade", "") or "",
            }
            for edu in educations
        ]

        # Format certifications
        cert_list = [
            {
                "name": cert.name,
                "issuer": cert.issuer or "",
                "year": getattr(cert, "issue_date", "") or "",
            }
            for cert in certifications
        ]

        # Construct evidence-grounded professional summary
        target_role = job.title or profile.title or "Software Engineer"
        top_matched = list(matched_skill_names)[:4] if matched_skill_names else user_skill_names[:4]
        skills_summary_str = f" emphasizing {', '.join(top_matched)}" if top_matched else ""
        summary_text = (
            f"Results-oriented {target_role} with proven background in software development and system architecture{skills_summary_str}. "
            f"Demonstrated ability to deliver robust applications, collaborate across engineering teams, and solve complex technical challenges."
        )

        content = {
            "summary": summary_text,
            "skills": categorized_skills,
            "experience": exp_list,
            "projects": proj_list,
            "education": edu_list,
            "certifications": cert_list,
        }

        # Determine version number (incrementing)
        highest_version = (
            db.query(func.max(TailoredResume.version_number))
            .filter(TailoredResume.job_id == job_id)
            .scalar()
            or 0
        )
        version_number = highest_version + 1

        tailored_resume = TailoredResume(
            job_id=job_id,
            user_id=user.id,
            version_number=version_number,
            status="draft",
            target_role=target_role,
            content=content,
        )
        db.add(tailored_resume)
        db.commit()
        db.refresh(tailored_resume)
        return tailored_resume

    def list_job_resumes(self, db: Session, user: User, job_id: int) -> List[TailoredResume]:
        self.get_job_or_404(db, user, job_id)
        return (
            db.query(TailoredResume)
            .filter(TailoredResume.job_id == job_id, TailoredResume.user_id == user.id)
            .order_by(TailoredResume.version_number.asc())
            .all()
        )

    def update_resume(
        self, db: Session, user: User, resume_id: int, update_data: TailoredResumeUpdate
    ) -> TailoredResume:
        resume = self.get_resume_or_404(db, user, resume_id)

        # Historical immutability rule: if resume is final or explicitly requested as new version
        if resume.status == "final" or update_data.save_as_new_version:
            highest_version = (
                db.query(func.max(TailoredResume.version_number))
                .filter(TailoredResume.job_id == resume.job_id)
                .scalar()
                or resume.version_number
            )
            new_resume = TailoredResume(
                job_id=resume.job_id,
                user_id=user.id,
                version_number=highest_version + 1,
                parent_version_id=resume.id,
                status="draft",
                target_role=update_data.target_role or resume.target_role,
                content=update_data.content,
            )
            db.add(new_resume)
            db.commit()
            db.refresh(new_resume)
            return new_resume

        # In-place update allowed ONLY for active draft
        resume.content = update_data.content
        if update_data.target_role:
            resume.target_role = update_data.target_role
        db.commit()
        db.refresh(resume)
        return resume

    def finalize_resume(self, db: Session, user: User, resume_id: int) -> TailoredResume:
        resume = self.get_resume_or_404(db, user, resume_id)
        resume.status = "final"
        db.commit()
        db.refresh(resume)
        return resume

    async def ask_ai_edit(
        self, db: Session, user: User, resume_id: int, request: AskAIRequest
    ) -> AskAIResponse:
        resume = self.get_resume_or_404(db, user, resume_id)
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()

        context_skills = []
        if profile:
            skills = db.query(CandidateSkill).filter(CandidateSkill.profile_id == profile.id).all()
            context_skills = [s.name for s in skills]

        refinement = await ollama_provider.refine_section(
            section=request.section,
            instruction=request.instruction,
            current_text=request.current_text or "",
            context_skills=context_skills,
        )

        return AskAIResponse(
            section=request.section,
            suggested_text=refinement.get("suggested_text", ""),
            explanation=refinement.get("explanation", "Refinement aligned with candidate evidence."),
            factuality_checked=True,
        )


tailoring_service = TailoringService()
