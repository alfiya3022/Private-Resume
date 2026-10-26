
from pathlib import Path
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
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
from app.models.artifact import ResumeArtifact
from app.models.validation import ResumeValidation
from app.schemas.tailored_resume import (
    TailoredResumeUpdate,
    AskAIRequest,
    AskAIResponse,
)
from app.services.ai.ollama_provider import (
    ollama_provider,
    TECH_CATEGORIES,
    CANONICAL_NAMES,
)


class TailoringService:
    def get_job_or_404(self, db: Session, user: User, job_id: int) -> Job:
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.user_id == user.id,
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or access unauthorized",
            )

        return job

    def get_resume_or_404(
        self,
        db: Session,
        user: User,
        resume_id: int,
    ) -> TailoredResume:
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

    def _invalidate_resume_artifacts(
        self,
        db: Session,
        user_id: int,
        resume_id: int,
    ) -> List[Path]:
        """Remove artifact and validation records for an edited draft."""
        artifacts = db.query(ResumeArtifact).filter(
            ResumeArtifact.tailored_resume_id == resume_id,
            ResumeArtifact.user_id == user_id,
        ).all()

        artifact_paths = [
            Path(artifact.file_path)
            for artifact in artifacts
            if artifact.file_path
        ]

        for artifact in artifacts:
            db.delete(artifact)

        db.query(ResumeValidation).filter(
            ResumeValidation.tailored_resume_id == resume_id,
            ResumeValidation.user_id == user_id,
        ).delete(synchronize_session=False)

        return artifact_paths

    def _remove_unreferenced_artifact_files(
        self,
        db: Session,
        artifact_paths: List[Path],
    ) -> None:
        """Remove files only when no artifact record references them."""
        for artifact_path in set(artifact_paths):
            still_referenced = db.query(ResumeArtifact.id).filter(
                ResumeArtifact.file_path == str(artifact_path),
            ).first()

            if still_referenced:
                continue

            try:
                artifact_path.unlink(missing_ok=True)
            except OSError:
                # The artifact record has already been invalidated.
                pass

    async def generate_initial_tailored_resume(
        self,
        db: Session,
        user: User,
        job_id: int,
    ) -> TailoredResume:
        job = self.get_job_or_404(db, user, job_id)

        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == user.id,
        ).first()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Candidate profile required before tailoring a resume. "
                    "Please upload a master resume or create your profile."
                ),
            )

        # Pull candidate data.
        candidate_skills = db.query(CandidateSkill).filter(
            CandidateSkill.profile_id == profile.id,
        ).all()

        experiences = db.query(Experience).filter(
            Experience.profile_id == profile.id,
        ).order_by(Experience.id.desc()).all()

        projects = db.query(Project).filter(
            Project.profile_id == profile.id,
        ).order_by(Project.id.desc()).all()

        educations = db.query(Education).filter(
            Education.profile_id == profile.id,
        ).all()

        certifications = db.query(Certification).filter(
            Certification.profile_id == profile.id,
        ).all()

        # Match analysis if present.
        match = db.query(MatchAnalysis).filter(
            MatchAnalysis.job_id == job_id,
        ).first()

        matched_skill_names = set(match.matched_skills if match else [])

        # Categorize candidate skills from profile evidence.
        categorized_skills: Dict[str, List[str]] = {
            "Languages": [],
            "Frameworks": [],
            "Databases": [],
            "Cloud & DevOps": [],
            "Tools": [],
            "Other": [],
        }

        user_skill_names = []

        for skill in candidate_skills:
            name = skill.name
            user_skill_names.append(name)
            name_lower = name.lower()
            placed = False

            for category, keywords in TECH_CATEGORIES.items():
                if name_lower in keywords or any(
                    keyword in name_lower for keyword in keywords
                ):
                    if category == "languages":
                        categorized_skills["Languages"].append(name)
                    elif category == "frameworks":
                        categorized_skills["Frameworks"].append(name)
                    elif category == "databases":
                        categorized_skills["Databases"].append(name)
                    elif category in ("cloud", "tools"):
                        categorized_skills["Cloud & DevOps"].append(name)

                    placed = True
                    break

            if not placed:
                categorized_skills["Other"].append(name)

        # Remove empty categories.
        categorized_skills = {
            key: value
            for key, value in categorized_skills.items()
            if value
        }

        # Format experience using only supplied evidence.
        exp_list = []

        for experience in experiences:
            exp_bullets = list(experience.bullets or [])

            if not exp_bullets and experience.description:
                exp_bullets = [
                    bullet.strip()
                    for bullet in experience.description.splitlines()
                    if bullet.strip()
                ]

            exp_list.append({
                "company": experience.company,
                "title": experience.title,
                "location": experience.location or "",
                "start_date": experience.start_date or "",
                "end_date": experience.end_date or "Present",
                "bullets": exp_bullets,
            })

        # Format projects using only supplied evidence.
        proj_list = []

        for project in projects:
            p_bullets = list(project.bullets or [])

            if not p_bullets and project.description:
                p_bullets = [
                    bullet.strip()
                    for bullet in project.description.splitlines()
                    if bullet.strip()
                ]

            proj_list.append({
                "name": project.title,
                "technologies": project.technologies or [],
                "description": project.description or "",
                "bullets": p_bullets,
                "link": getattr(project, "url", "") or "",
                "github_url": getattr(project, "github_url", "") or getattr(project, "url", "") or "",
                "start_date": getattr(project, "start_date", "") or "",
                "end_date": getattr(project, "end_date", "") or "",
            })

        # Format education.
        edu_list = [
            {
                "institution": education.institution,
                "degree": education.degree,
                "year": getattr(education, "end_date", "") or "",
                "gpa": getattr(education, "grade", "") or "",
            }
            for education in educations
        ]

        # Format certifications.
        cert_list = [
            {
                "name": certification.name,
                "issuer": certification.issuer or "",
                "year": getattr(certification, "issue_date", "") or "",
                "certificate_url": getattr(certification, "credential_url", "") or getattr(certification, "certificate_url", "") or "",
            }
            for certification in certifications
        ]

        # Build a summary from candidate-provided skills only.
        # Do not invent experience, achievements, or technical claims.
        target_role = job.title or profile.title or "Software Engineer"
        top_matched = [
            skill for skill in user_skill_names
            if skill in matched_skill_names
        ][:4]

        if not top_matched:
            top_matched = user_skill_names[:4]

        summary_text = (
            f"Targeting {target_role}, with skills in "
            f"{', '.join(top_matched)}."
            if top_matched
            else ""
        )

        content = {
            "summary": summary_text,
            "skills": categorized_skills,
            "experience": exp_list,
            "projects": proj_list,
            "education": edu_list,
            "certifications": cert_list,
        }

        # Determine version number.
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

    def list_job_resumes(
        self,
        db: Session,
        user: User,
        job_id: int,
    ) -> List[TailoredResume]:
        self.get_job_or_404(db, user, job_id)

        return (
            db.query(TailoredResume)
            .filter(
                TailoredResume.job_id == job_id,
                TailoredResume.user_id == user.id,
            )
            .order_by(TailoredResume.version_number.asc())
            .all()
        )

    def update_resume(
        self,
        db: Session,
        user: User,
        resume_id: int,
        update_data: TailoredResumeUpdate,
    ) -> TailoredResume:
        resume = self.get_resume_or_404(db, user, resume_id)

        # Preserve historical immutability for finalized resumes.
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

        # In-place update is allowed only for an active draft.
        artifact_paths = self._invalidate_resume_artifacts(
            db,
            user.id,
            resume.id,
        )

        resume.content = dict(update_data.content)
        flag_modified(resume, "content")

        if update_data.target_role:
            resume.target_role = update_data.target_role

        db.commit()
        db.refresh(resume)

        # Remove old files only after the database update succeeds.
        self._remove_unreferenced_artifact_files(db, artifact_paths)

        return resume

    def finalize_resume(
        self,
        db: Session,
        user: User,
        resume_id: int,
    ) -> TailoredResume:
        resume = self.get_resume_or_404(db, user, resume_id)
        resume.status = "final"

        db.commit()
        db.refresh(resume)

        return resume

    async def ask_ai_edit(
        self,
        db: Session,
        user: User,
        resume_id: int,
        request: AskAIRequest,
    ) -> AskAIResponse:
        resume = self.get_resume_or_404(db, user, resume_id)

        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == user.id,
        ).first()

        candidate_evidence: Dict[str, Any] = {
            "skills": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "education": [],
        }

        if profile:
            skills = db.query(CandidateSkill).filter(
                CandidateSkill.profile_id == profile.id,
            ).all()
            candidate_evidence["skills"] = [skill.name for skill in skills]

            experiences = db.query(Experience).filter(
                Experience.profile_id == profile.id,
            ).all()
            candidate_evidence["experience"] = [
                f"{exp.title} at {exp.company}: {exp.description or ''}"
                for exp in experiences
            ]

            projects = db.query(Project).filter(
                Project.profile_id == profile.id,
            ).all()
            candidate_evidence["projects"] = [
                f"{proj.title}: {proj.description or ''} (Tech: {', '.join(proj.technologies or [])})"
                for proj in projects
            ]

            certs = db.query(Certification).filter(
                Certification.profile_id == profile.id,
            ).all()
            candidate_evidence["certifications"] = [
                f"{c.name} by {c.issuer or ''}" for c in certs
            ]

            edus = db.query(Education).filter(
                Education.profile_id == profile.id,
            ).all()
            candidate_evidence["education"] = [
                f"{e.degree} from {e.institution}" for e in edus
            ]

        refinement = await ollama_provider.refine_section(
            section=request.section,
            instruction=request.instruction,
            current_text=request.current_text or "",
            candidate_evidence=candidate_evidence,
            context_skills=candidate_evidence["skills"],
            acknowledge_unsupported=request.acknowledge_unsupported,
        )

        return AskAIResponse(
            section=request.section,
            suggested_text=refinement.get("suggested_text", ""),
            explanation=refinement.get(
                "explanation",
                "Refinement aligned with candidate evidence.",
            ),
            factuality_checked=True,
            has_unsupported_content=refinement.get("has_unsupported_content", False),
            missing_evidence=refinement.get("missing_evidence", []),
            evidence_warning=refinement.get("evidence_warning"),
        )


tailoring_service = TailoringService()
