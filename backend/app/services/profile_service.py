from datetime import datetime, timezone
import difflib
import re
from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status

from app.models.profile import (
    CandidateProfile,
    CandidateSkill,
    Project,
    Experience,
    Education,
    Certification,
    CareerKnowledgeItem,
)
from app.models.user import User
from app.models.resume import MasterResume
from app.schemas.profile import (
    ProfileUpdate,
    SkillCreate,
    ProjectCreate,
    ExperienceCreate,
    EducationCreate,
    CertificationCreate,
)
from app.services.storage_service import storage_service
from app.services.pdf_service import pdf_service
from app.services.career_knowledge_service import career_knowledge_service
from rapidfuzz import fuzz


def normalize_project_title(title: str) -> str:
    """Normalize project title: lowercase, strip badge text like [GitHub] or [Live], strip non-alphanumeric."""
    if not title:
        return ""
    cleaned = re.sub(r"\[.*?\]", "", title)
    cleaned = cleaned.lower()
    cleaned = re.sub(r"[^a-z0-9]", "", cleaned)
    return cleaned


def is_same_project_title(t1: str, t2: str) -> bool:
    """Compare two project titles by normalized equality or SequenceMatcher ratio >= 0.9."""
    norm1 = normalize_project_title(t1)
    norm2 = normalize_project_title(t2)
    if not norm1 or not norm2:
        return False
    if norm1 == norm2:
        return True
    return difflib.SequenceMatcher(None, norm1, norm2).ratio() >= 0.9


def normalize_url(url: Optional[str]) -> str:
    """Normalize project/live URL for comparison and deduplication."""
    if not url:
        return ""
    u = str(url).strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = u.rstrip("/")
    u = re.sub(r"\.git$", "", u)
    return u.rstrip("/")


def compare_projects_multi_signal(incoming_p: Dict[str, Any], existing_p: Project) -> Dict[str, Any]:
    """Multi-signal comparison between an incoming project dict and an existing profile Project.
    
    Signals:
    - Repository/Live URL identity
    - Normalized title similarity & fuzzy token set ratio
    - Technology stack overlap (Jaccard)
    """
    inc_title = (incoming_p.get("title") or "").strip()
    ext_title = (existing_p.title or "").strip()

    inc_url = normalize_url(incoming_p.get("url") or incoming_p.get("github_url") or incoming_p.get("live_url"))
    ext_url = normalize_url(existing_p.url)

    url_match = bool(inc_url and ext_url and inc_url == ext_url)

    norm_inc = normalize_project_title(inc_title)
    norm_ext = normalize_project_title(ext_title)
    title_exact = bool(norm_inc and norm_inc == norm_ext)

    title_ratio = (
        fuzz.token_set_ratio(inc_title.lower(), ext_title.lower()) / 100.0
        if (inc_title and ext_title)
        else 0.0
    )

    inc_tech = set(str(t).lower().strip() for t in (incoming_p.get("technologies") or []))
    ext_tech = set(str(t).lower().strip() for t in (existing_p.technologies or []))
    tech_jaccard = 0.0
    if inc_tech and ext_tech:
        union = inc_tech | ext_tech
        if union:
            tech_jaccard = len(inc_tech & ext_tech) / len(union)

    if title_exact:
        return {
            "status": "same",
            "score": 1.0,
            "reason": "Exact matching project title",
            "existing_id": existing_p.id,
            "existing_title": ext_title,
        }

    if url_match:
        if title_ratio >= 0.80:
            return {
                "status": "same",
                "score": 0.95,
                "reason": f"Matching repository URL ({inc_url}) and project title",
                "existing_id": existing_p.id,
                "existing_title": ext_title,
            }
        else:
            return {
                "status": "possible_duplicate",
                "score": 0.85,
                "reason": f"Same repository URL ({inc_url}) with differing title ('{ext_title}')",
                "existing_id": existing_p.id,
                "existing_title": ext_title,
            }

    if title_ratio >= 0.88 or (title_ratio >= 0.75 and tech_jaccard >= 0.35):
        return {
            "status": "possible_duplicate",
            "score": round(title_ratio, 2),
            "reason": f"Similar project title ({int(title_ratio*100)}%) and overlapping tech stack",
            "existing_id": existing_p.id,
            "existing_title": ext_title,
        }

    return {
        "status": "different",
        "score": 0.0,
        "reason": "Distinct project",
        "existing_id": existing_p.id,
        "existing_title": ext_title,
    }


class ProfileService:
    @staticmethod
    def get_or_create_profile(db: Session, user_id: int) -> CandidateProfile:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if not profile:
            profile = CandidateProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @classmethod
    def update_profile(
        cls, db: Session, user_id: int, profile_in: ProfileUpdate
    ) -> CandidateProfile:
        profile = cls.get_or_create_profile(db, user_id)
        update_data = profile_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
        return profile

    # Sub-item management
    @classmethod
    def add_skill(cls, db: Session, user_id: int, skill_in: SkillCreate) -> CandidateSkill:
        profile = cls.get_or_create_profile(db, user_id)
        skill = CandidateSkill(
            profile_id=profile.id,
            name=skill_in.name.strip(),
            category=skill_in.category,
            proficiency=skill_in.proficiency,
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    @classmethod
    def delete_skill(cls, db: Session, user_id: int, skill_id: int) -> bool:
        profile = cls.get_or_create_profile(db, user_id)
        skill = db.query(CandidateSkill).filter(
            CandidateSkill.id == skill_id, CandidateSkill.profile_id == profile.id
        ).first()
        if not skill:
            return False
        db.delete(skill)
        db.commit()
        return True

    @classmethod
    def add_project(cls, db: Session, user_id: int, proj_in: ProjectCreate) -> Project:
        profile = cls.get_or_create_profile(db, user_id)
        project = Project(
            profile_id=profile.id,
            title=proj_in.title,
            role=proj_in.role,
            description=proj_in.description,
            bullets=proj_in.bullets,
            technologies=proj_in.technologies,
            url=proj_in.url,
            start_date=proj_in.start_date,
            end_date=proj_in.end_date,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @classmethod
    def update_project(cls, db: Session, user_id: int, project_id: int, project_in: Any) -> Optional[Project]:
        profile = cls.get_or_create_profile(db, user_id)
        project = db.query(Project).filter(
            Project.id == project_id, Project.profile_id == profile.id
        ).first()
        if not project:
            return None
        update_data = project_in.model_dump(exclude_unset=True) if hasattr(project_in, "model_dump") else dict(project_in)
        for field, value in update_data.items():
            if hasattr(project, field) and value is not None:
                setattr(project, field, value)
        db.commit()
        db.refresh(project)
        return project

    @classmethod
    def delete_project(cls, db: Session, user_id: int, project_id: int) -> bool:
        profile = cls.get_or_create_profile(db, user_id)
        project = db.query(Project).filter(
            Project.id == project_id, Project.profile_id == profile.id
        ).first()
        if not project:
            return False
        db.delete(project)
        db.commit()
        return True

    @classmethod
    def add_experience(cls, db: Session, user_id: int, exp_in: ExperienceCreate) -> Experience:
        profile = cls.get_or_create_profile(db, user_id)
        exp = Experience(
            profile_id=profile.id,
            company=exp_in.company,
            title=exp_in.title,
            location=exp_in.location,
            description=exp_in.description,
            bullets=exp_in.bullets,
            start_date=exp_in.start_date,
            end_date=exp_in.end_date,
            is_current=exp_in.is_current,
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)
        return exp

    @classmethod
    def update_experience(cls, db: Session, user_id: int, exp_id: int, exp_in: Any) -> Optional[Experience]:
        profile = cls.get_or_create_profile(db, user_id)
        exp = db.query(Experience).filter(
            Experience.id == exp_id, Experience.profile_id == profile.id
        ).first()
        if not exp:
            return None
        update_data = exp_in.model_dump(exclude_unset=True) if hasattr(exp_in, "model_dump") else dict(exp_in)
        for field, value in update_data.items():
            if hasattr(exp, field) and value is not None:
                setattr(exp, field, value)
        db.commit()
        db.refresh(exp)
        return exp

    @classmethod
    def delete_experience(cls, db: Session, user_id: int, exp_id: int) -> bool:
        profile = cls.get_or_create_profile(db, user_id)
        exp = db.query(Experience).filter(
            Experience.id == exp_id, Experience.profile_id == profile.id
        ).first()
        if not exp:
            return False
        db.delete(exp)
        db.commit()
        return True

    @classmethod
    def add_education(cls, db: Session, user_id: int, edu_in: EducationCreate) -> Education:
        profile = cls.get_or_create_profile(db, user_id)
        edu = Education(
            profile_id=profile.id,
            institution=edu_in.institution,
            degree=edu_in.degree,
            field_of_study=edu_in.field_of_study,
            grade=edu_in.grade,
            start_date=edu_in.start_date,
            end_date=edu_in.end_date,
        )
        db.add(edu)
        db.commit()
        db.refresh(edu)
        return edu

    @classmethod
    def update_education(cls, db: Session, user_id: int, edu_id: int, edu_in: Any) -> Optional[Education]:
        profile = cls.get_or_create_profile(db, user_id)
        edu = db.query(Education).filter(
            Education.id == edu_id, Education.profile_id == profile.id
        ).first()
        if not edu:
            return None
        update_data = edu_in.model_dump(exclude_unset=True) if hasattr(edu_in, "model_dump") else dict(edu_in)
        for field, value in update_data.items():
            if hasattr(edu, field) and value is not None:
                setattr(edu, field, value)
        db.commit()
        db.refresh(edu)
        return edu

    @classmethod
    def delete_education(cls, db: Session, user_id: int, edu_id: int) -> bool:
        profile = cls.get_or_create_profile(db, user_id)
        edu = db.query(Education).filter(
            Education.id == edu_id, Education.profile_id == profile.id
        ).first()
        if not edu:
            return False
        db.delete(edu)
        db.commit()
        return True

    @classmethod
    def add_certification(
        cls, db: Session, user_id: int, cert_in: CertificationCreate
    ) -> Certification:
        profile = cls.get_or_create_profile(db, user_id)
        cert = Certification(
            profile_id=profile.id,
            name=cert_in.name,
            issuer=cert_in.issuer,
            issue_date=cert_in.issue_date,
            credential_url=cert_in.credential_url,
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)
        return cert

    @classmethod
    def update_certification(cls, db: Session, user_id: int, cert_id: int, cert_in: Any) -> Optional[Certification]:
        profile = cls.get_or_create_profile(db, user_id)
        cert = db.query(Certification).filter(
            Certification.id == cert_id, Certification.profile_id == profile.id
        ).first()
        if not cert:
            return None
        update_data = cert_in.model_dump(exclude_unset=True) if hasattr(cert_in, "model_dump") else dict(cert_in)
        for field, value in update_data.items():
            if hasattr(cert, field) and value is not None:
                setattr(cert, field, value)
        db.commit()
        db.refresh(cert)
        return cert

    @classmethod
    def delete_certification(cls, db: Session, user_id: int, cert_id: int) -> bool:
        profile = cls.get_or_create_profile(db, user_id)
        cert = db.query(Certification).filter(
            Certification.id == cert_id, Certification.profile_id == profile.id
        ).first()
        if not cert:
            return False
        db.delete(cert)
        db.commit()
        return True

    @classmethod
    def reset_section(cls, db: Session, user_id: int, section: str) -> CandidateProfile:
        """Permanently delete all persisted records in a specific profile section for the user."""
        profile = cls.get_or_create_profile(db, user_id)
        norm_section = section.lower().strip()

        if norm_section in ("personal", "personal_info"):
            profile.headline = None
            profile.summary = None
            profile.phone = None
            profile.location = None
            profile.linkedin_url = None
            profile.github_url = None
            profile.portfolio_url = None
        elif norm_section == "skills":
            db.query(CandidateSkill).filter(
                CandidateSkill.profile_id == profile.id
            ).delete(synchronize_session="fetch")
        elif norm_section == "projects":
            db.query(Project).filter(
                Project.profile_id == profile.id
            ).delete(synchronize_session="fetch")
        elif norm_section in ("experience", "experiences"):
            db.query(Experience).filter(
                Experience.profile_id == profile.id
            ).delete(synchronize_session="fetch")
        elif norm_section in ("education", "educations"):
            db.query(Education).filter(
                Education.profile_id == profile.id
            ).delete(synchronize_session="fetch")
        elif norm_section in ("certifications", "certification"):
            db.query(Certification).filter(
                Certification.profile_id == profile.id
            ).delete(synchronize_session="fetch")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown profile section '{section}'",
            )

        db.commit()
        db.refresh(profile)
        return profile

    @classmethod
    def reset_all(cls, db: Session, user_id: int) -> CandidateProfile:
        """Permanently delete all persisted records across all six profile sections for the user."""
        profile = cls.get_or_create_profile(db, user_id)

        # Clear personal info metadata
        profile.headline = None
        profile.summary = None
        profile.phone = None
        profile.location = None
        profile.linkedin_url = None
        profile.github_url = None
        profile.portfolio_url = None

        # Delete all child items in an atomic transaction
        db.query(CandidateSkill).filter(
            CandidateSkill.profile_id == profile.id
        ).delete(synchronize_session="fetch")
        db.query(Project).filter(
            Project.profile_id == profile.id
        ).delete(synchronize_session="fetch")
        db.query(Experience).filter(
            Experience.profile_id == profile.id
        ).delete(synchronize_session="fetch")
        db.query(Education).filter(
            Education.profile_id == profile.id
        ).delete(synchronize_session="fetch")
        db.query(Certification).filter(
            Certification.profile_id == profile.id
        ).delete(synchronize_session="fetch")

        db.commit()
        db.refresh(profile)
        return profile

    # Master Resume workflows
    @classmethod
    async def prepare_master_resume_upload(
        cls, db: Session, user_id: int, file: UploadFile, replace: bool = False
    ) -> MasterResume:
        """Saves uploaded PDF and creates/updates MasterResume record in queued state."""
        existing_resume = (
            db.query(MasterResume).filter(MasterResume.user_id == user_id).first()
        )
        if existing_resume and not replace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A Master Resume already exists. Only one Master Resume is allowed per user. Please delete or replace the existing resume.",
            )

        file_path, file_size = await storage_service.save_resume_file(user_id, file)

        if existing_resume and replace:
            if existing_resume.file_path and existing_resume.file_path != file_path:
                storage_service.delete_file(existing_resume.file_path)

            existing_resume.filename = file.filename
            existing_resume.file_path = file_path
            existing_resume.file_size = file_size
            existing_resume.raw_text = ""
            existing_resume.extracted_data = {}
            existing_resume.parse_status = "queued"
            existing_resume.parse_stage = "Queued"
            existing_resume.parse_error = None
            existing_resume.parse_started_at = datetime.now(timezone.utc)
            existing_resume.parse_finished_at = None
            existing_resume.is_active = True
            db.commit()
            db.refresh(existing_resume)
            return existing_resume
        else:
            resume = MasterResume(
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                raw_text="",
                extracted_data={},
                parse_status="queued",
                parse_stage="Queued",
                parse_error=None,
                parse_started_at=datetime.now(timezone.utc),
                is_active=True,
            )
            db.add(resume)
            db.commit()
            db.refresh(resume)
            return resume

    @classmethod
    def process_master_resume_background(cls, resume_id: int, user_id: int) -> None:
        """Executes background extraction stages and updates resume status in database."""
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            resume = db.query(MasterResume).filter(
                MasterResume.id == resume_id, MasterResume.user_id == user_id
            ).first()
            if not resume:
                return

            # Stage 1: Reading layout and text
            resume.parse_status = "running"
            resume.parse_stage = "Reading layout and text"
            db.commit()

            raw_text = pdf_service.extract_text_from_pdf(resume.file_path)

            # Stage 2: Segmenting sections
            resume.parse_stage = "Segmenting sections"
            db.commit()

            # Stage 3: Extracting skills and entities
            resume.parse_stage = "Extracting skills and entities"
            db.commit()

            user_corrections = career_knowledge_service.get_user_corrections(db, user_id)
            extracted_data = pdf_service.extract_full_resume_data(
                resume.file_path, raw_text=raw_text, user_corrections=user_corrections
            )

            # Stage 4: Resolving career knowledge
            resume.parse_stage = "Resolving career knowledge"
            db.commit()

            # Complete
            resume.raw_text = raw_text
            resume.extracted_data = extracted_data
            resume.parse_status = "complete"
            resume.parse_stage = "Complete"
            resume.parse_finished_at = datetime.now(timezone.utc)
            resume.parse_error = None
            db.commit()
        except Exception as exc:
            logger.error(f"Error parsing resume {resume_id}: {exc}")
            try:
                resume = db.query(MasterResume).filter(MasterResume.id == resume_id).first()
                if resume:
                    resume.parse_status = "failed"
                    resume.parse_stage = "Failed"
                    resume.parse_error = "Could not parse text or structured data from uploaded PDF"
                    resume.parse_finished_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception:
                pass
        finally:
            db.close()

    @classmethod
    async def process_master_resume_upload(
        cls, db: Session, user_id: int, file: UploadFile, replace: bool = False
    ) -> MasterResume:
        # Check if an existing master resume already exists for the user
        existing_resume = (
            db.query(MasterResume).filter(MasterResume.user_id == user_id).first()
        )
        if existing_resume and not replace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A Master Resume already exists. Only one Master Resume is allowed per user. Please delete or replace the existing resume.",
            )

        # 1. Save file locally
        file_path, file_size = await storage_service.save_resume_file(user_id, file)

        # 2. Extract plain text and layout data with PyMuPDF
        try:
            plain_text = pdf_service.extract_text_from_pdf_plain(file_path)
            raw_text = pdf_service.extract_text_from_pdf(file_path)
            extracted_data = await pdf_service.extract_full_resume_data_hybrid(
                file_path, raw_text, plain_text=plain_text
            )
        except Exception as e:
            storage_service.delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not parse text or structured data from uploaded PDF: {str(e)}",
            )

        if existing_resume and replace:
            if existing_resume.file_path and existing_resume.file_path != file_path:
                storage_service.delete_file(existing_resume.file_path)

            existing_resume.filename = file.filename
            existing_resume.file_path = file_path
            existing_resume.file_size = file_size
            existing_resume.raw_text = raw_text
            existing_resume.extracted_data = extracted_data
            existing_resume.parse_status = "complete"
            existing_resume.parse_stage = "Complete"
            existing_resume.parse_finished_at = datetime.now(timezone.utc)
            existing_resume.is_active = True
            db.commit()
            db.refresh(existing_resume)
            resume = existing_resume
        else:
            resume = MasterResume(
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                raw_text=raw_text,
                extracted_data=extracted_data,
                parse_status="complete",
                parse_stage="Complete",
                parse_started_at=datetime.now(timezone.utc),
                parse_finished_at=datetime.now(timezone.utc),
                is_active=True,
            )
            db.add(resume)
            db.commit()
            db.refresh(resume)

        return resume

    @classmethod
    def compare_extracted_data_with_profile(
        cls, profile: CandidateProfile, extracted_data: Dict[str, Any], db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Compares extracted resume data against current profile and generates diff/conflict report."""
        if not extracted_data:
            return {}

        extracted_p = extracted_data.get("personal_info") or {}
        personal_diff = {}

        # Look up user record for name/email comparison if db provided
        user_obj = None
        if db is not None:
            user_obj = db.query(User).filter(User.id == profile.user_id).first()

        for field in [
            "name",
            "email",
            "headline",
            "summary",
            "phone",
            "location",
            "linkedin_url",
            "github_url",
            "portfolio_url",
        ]:
            if field == "name":
                curr = (user_obj.full_name if user_obj else "") or ""
                extr = extracted_p.get("name") or extracted_p.get("full_name") or ""
            elif field == "email":
                curr = (user_obj.email if user_obj else "") or ""
                extr = extracted_p.get("email") or ""
            elif field == "summary":
                curr = getattr(profile, "summary", "") or ""
                extr = extracted_data.get("summary") or extracted_p.get("summary") or ""
            else:
                curr = getattr(profile, field, "") or ""
                extr = extracted_p.get(field) or ""

            if not curr and extr:
                s_code = "new"
            elif curr and extr and str(curr).strip().lower() != str(extr).strip().lower():
                s_code = "conflict"
            elif curr and not extr:
                s_code = "current_only"
            elif curr and extr:
                s_code = "match"
            else:
                s_code = "empty"
            personal_diff[field] = {
                "current": curr,
                "extracted": extr,
                "status": s_code,
            }

        # Skills comparison using career knowledge, aliases, distinct pairs, and prior corrections
        existing_skills_map = {s.name.lower(): s for s in profile.skills}
        extracted_skills = extracted_data.get("skills") or []
        new_skills = []
        matching_skills = []
        possible_dup_skills = []

        for s in extracted_skills:
            s_name = s.get("name", "") if isinstance(s, dict) else str(s)
            s_clean = s_name.strip()
            if not s_clean:
                continue

            if s_clean.lower() in existing_skills_map:
                matching_skills.append(s)
                continue

            # Classify relationship against profile skills
            best_rel = None
            matched_profile_name = None
            for ex_name, ex_skill in existing_skills_map.items():
                rel = career_knowledge_service.classify_relationship(s_clean, ex_skill.name)
                if rel.get("is_match"):
                    if best_rel is None or rel.get("score", 0) > best_rel.get("score", 0):
                        best_rel = rel
                        matched_profile_name = ex_skill.name

            if best_rel and matched_profile_name:
                if best_rel.get("relationship") in ("Exact match", "Known alias"):
                    matching_skills.append(s)
                else:
                    possible_dup_skills.append({
                        "skill": s,
                        "matched_with": matched_profile_name,
                        "relationship": best_rel.get("relationship"),
                        "score": best_rel.get("score"),
                    })
            else:
                new_skills.append(s)

        skills_diff = {
            "new_skills": new_skills,
            "matching_skills": matching_skills,
            "possible_duplicates": possible_dup_skills,
            "total_extracted": len(extracted_skills),
        }

        # Projects multi-signal comparison
        extracted_projs = extracted_data.get("projects") or []
        projects_diff = {
            "new_items": [],
            "matching_items": [],
            "possible_duplicates": [],
            "total_extracted": len(extracted_projs),
        }

        for idx, p in enumerate(extracted_projs):
            best_match = None
            for ep in profile.projects:
                comp = compare_projects_multi_signal(p, ep)
                if comp["status"] in ("same", "possible_duplicate"):
                    if best_match is None or comp["score"] > best_match["score"]:
                        best_match = comp

            item_entry = dict(p)
            item_entry["incoming_index"] = idx
            if best_match:
                item_entry["match"] = best_match
                if best_match["status"] == "same":
                    projects_diff["matching_items"].append(item_entry)
                else:
                    projects_diff["possible_duplicates"].append(item_entry)
            else:
                projects_diff["new_items"].append(item_entry)

        existing_exp_keys = {
            ((e.company or "") + "|" + (e.title or "")).strip().lower()
            for e in profile.experiences
        }
        extracted_exps = extracted_data.get("experience") or []
        experience_diff = {
            "new_items": [
                e for e in extracted_exps
                if ((e.get("company") or "") + "|" + (e.get("title") or "")).strip().lower() not in existing_exp_keys
            ],
            "matching_items": [
                e for e in extracted_exps
                if ((e.get("company") or "") + "|" + (e.get("title") or "")).strip().lower() in existing_exp_keys
            ],
            "total_extracted": len(extracted_exps),
        }

        existing_edu_keys = {
            ((ed.institution or "") + "|" + (ed.degree or "")).strip().lower()
            for ed in profile.educations
        }
        extracted_edus = extracted_data.get("education") or []
        education_diff = {
            "new_items": [
                ed for ed in extracted_edus
                if ((ed.get("institution") or "") + "|" + (ed.get("degree") or "")).strip().lower() not in existing_edu_keys
            ],
            "matching_items": [
                ed for ed in extracted_edus
                if ((ed.get("institution") or "") + "|" + (ed.get("degree") or "")).strip().lower() in existing_edu_keys
            ],
            "total_extracted": len(extracted_edus),
        }

        existing_cert_names = {(c.name or "").strip().lower() for c in profile.certifications}
        extracted_certs = extracted_data.get("certifications") or []
        certs_diff = {
            "new_items": [c for c in extracted_certs if (c.get("name") or "").strip().lower() not in existing_cert_names],
            "matching_items": [c for c in extracted_certs if (c.get("name") or "").strip().lower() in existing_cert_names],
            "total_extracted": len(extracted_certs),
        }

        return {
            "personal_info": personal_diff,
            "skills": skills_diff,
            "projects": projects_diff,
            "experience": experience_diff,
            "education": education_diff,
            "certifications": certs_diff,
        }

    @classmethod
    def get_resume_extracted_data(
        cls, db: Session, user_id: int, resume_id: int
    ) -> Dict[str, Any]:
        """Retrieves structured extracted data and comparison for a master resume."""
        resume = db.query(MasterResume).filter(
            MasterResume.id == resume_id, MasterResume.user_id == user_id
        ).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Master resume not found",
            )

        extracted = resume.extracted_data
        if not extracted:
            try:
                extracted = pdf_service.extract_full_resume_data(resume.file_path, resume.raw_text)
                resume.extracted_data = extracted
                db.commit()
            except Exception as e:
                extracted = {}

        profile = cls.get_or_create_profile(db, user_id)
        comparison = cls.compare_extracted_data_with_profile(profile, extracted, db=db)

        return {
            "resume_id": resume.id,
            "filename": resume.filename,
            "extracted_data": extracted,
            "comparison": comparison,
            "is_active": resume.is_active,
        }

    @classmethod
    def apply_extracted_data_to_profile(
        cls,
        db: Session,
        user_id: int,
        resume_id: int,
        sections: Optional[List[str]] = None,
        overwrite_existing: bool = False,
        edited_data: Optional[Dict[str, Any]] = None,
        item_decisions: Optional[Dict[str, str]] = None,
        remember_corrections: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Selectively applies approved extracted sections to candidate profile with per-item duplicate consent."""
        profile = cls.get_or_create_profile(db, user_id)
        resume = db.query(MasterResume).filter(
            MasterResume.id == resume_id, MasterResume.user_id == user_id
        ).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Master resume not found",
            )

        if remember_corrections:
            for corr in remember_corrections:
                career_knowledge_service.record_user_correction(
                    db=db,
                    user_id=user_id,
                    field_name=corr.get("field_name") or "correction",
                    original_value=corr.get("original_value") or "",
                    corrected_value=corr.get("corrected_value") or "",
                    category=corr.get("category"),
                )

        if edited_data:
            extracted = edited_data
            resume.extracted_data = edited_data
            db.commit()
        else:
            extracted = resume.extracted_data

        if not extracted:
            try:
                extracted = pdf_service.extract_full_resume_data(resume.file_path, resume.raw_text)
                resume.extracted_data = extracted
                db.commit()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Unable to extract data from master resume: {str(e)}",
                )

        selected_sections = sections if sections else [
            "personal_info",
            "skills",
            "education",
            "experience",
            "projects",
            "certifications",
        ]

        decisions = item_decisions or {}

        counts = {
            "personal_fields_updated": 0,
            "skills_added": 0,
            "education_added": 0,
            "education_updated": 0,
            "experience_added": 0,
            "experience_updated": 0,
            "projects_added": 0,
            "projects_updated": 0,
            "certifications_added": 0,
            "certifications_updated": 0,
        }

        # 1. Personal info
        if "personal_info" in selected_sections:
            p_info = extracted.get("personal_info") or {}
            for field in ["phone", "location", "linkedin_url", "github_url", "portfolio_url"]:
                new_val = p_info.get(field)
                if new_val and str(new_val).strip():
                    curr_val = getattr(profile, field, None)
                    if overwrite_existing or not curr_val or not str(curr_val).strip():
                        setattr(profile, field, str(new_val).strip())
                        counts["personal_fields_updated"] += 1
            if p_info.get("headline") and (overwrite_existing or not profile.headline):
                profile.headline = p_info["headline"]
                counts["personal_fields_updated"] += 1
            if (extracted.get("summary") or p_info.get("summary")) and (overwrite_existing or not profile.summary):
                profile.summary = extracted.get("summary") or p_info.get("summary")
                counts["personal_fields_updated"] += 1

            # Candidate full name
            cand_name = p_info.get("name") or p_info.get("full_name")
            if cand_name and str(cand_name).strip():
                user_record = db.query(User).filter(User.id == user_id).first()
                if user_record and (overwrite_existing or not user_record.full_name or not str(user_record.full_name).strip()):
                    user_record.full_name = str(cand_name).strip()
                    counts["personal_fields_updated"] += 1

        # 2. Skills
        if "skills" in selected_sections:
            existing_skills_map = {s.name.lower(): s for s in profile.skills}
            raw_skill_list = extracted.get("skills") or []
            
            # Safety net guard: parser output should already be split into atomic skills via
            # inferred document delimiters (2.6); keep this save-time guard only as a safety net.
            unpacked_skills = []
            for item in raw_skill_list:
                if isinstance(item, dict):
                    raw_nm = (item.get("name") or "").strip()
                    cat = (item.get("category") or "Other").strip()
                    ev = item.get("source_evidence")
                else:
                    raw_nm = str(item).strip()
                    cat = "Other"
                    ev = None

                # Inferred delimiters safety net split
                parts = re.split(r"[,;•●▪◦⋄·|\u2022\u00b7]+", raw_nm)
                for part in parts:
                    clean_p = part.strip()
                    if clean_p and len(clean_p) > 1:
                        unpacked_skills.append({
                            "name": clean_p[:100],
                            "category": (cat or "Other")[:100],
                            "source_evidence": ev,
                        })

            valid_skill_names = [s["name"] for s in unpacked_skills]
            # Pre-generate embeddings in one batch to prevent CPU timeout during apply
            skill_embeddings = career_knowledge_service.generate_embeddings_batch(valid_skill_names)
            embedding_lookup = {name: emb for name, emb in zip(valid_skill_names, skill_embeddings)}

            for item in unpacked_skills:
                skill_name = item.get("name")
                skill_cat = item.get("category") or "Other"
                evidence = item.get("source_evidence")

                if not skill_name or not str(skill_name).strip():
                    continue

                s_clean = str(skill_name).strip()[:100]
                s_lower = s_clean.lower()

                # Check per-item decision
                skill_decision = (
                    decisions.get(f"skills:{s_lower}")
                    or decisions.get(f"skill:{s_lower}")
                    or decisions.get(s_lower)
                )

                if skill_decision == "discard":
                    career_knowledge_service.record_user_correction(
                        db=db,
                        user_id=user_id,
                        field_name="skill",
                        original_value=s_clean,
                        corrected_value="[DISCARDED]",
                        category="discard",
                    )
                    continue

                # Record in career knowledge with pre-computed embedding
                career_knowledge_service.record_knowledge_item(
                    db=db,
                    user_id=user_id,
                    knowledge_type="skill",
                    source_type="user_profile",
                    source_id=str(resume_id),
                    original_text=s_clean,
                    category=skill_cat,
                    source_evidence=evidence,
                    review_status="confirmed",
                    embedding=embedding_lookup.get(s_clean),
                )

                if skill_decision == "replace_with_new":
                    if s_lower in existing_skills_map:
                        existing_skills_map[s_lower].category = skill_cat
                        existing_skills_map[s_lower].source_evidence = evidence
                    else:
                        new_sk = CandidateSkill(
                            profile_id=profile.id,
                            name=s_clean,
                            category=skill_cat,
                            proficiency="Intermediate",
                            source_evidence=evidence,
                            review_status="confirmed",
                        )
                        db.add(new_sk)
                        existing_skills_map[s_lower] = new_sk
                        counts["skills_added"] += 1
                elif skill_decision == "keep_existing":
                    # Retain profile version
                    pass
                else:
                    # Default: add if not present
                    if s_lower not in existing_skills_map:
                        new_sk = CandidateSkill(
                            profile_id=profile.id,
                            name=s_clean,
                            category=skill_cat,
                            proficiency="Intermediate",
                            source_evidence=evidence,
                            review_status="confirmed",
                        )
                        db.add(new_sk)
                        existing_skills_map[s_lower] = new_sk
                        counts["skills_added"] += 1

        # 3. Projects
        if "projects" in selected_sections:
            existing_projs = [p for p in profile.projects if p.title]

            for idx, proj_dict in enumerate(extracted.get("projects") or []):
                title = (proj_dict.get("title") or "").strip()
                if not title:
                    continue

                proj_decision = (
                    decisions.get(f"projects:{idx}")
                    or decisions.get(f"projects_{idx}")
                    or decisions.get(f"project:{idx}")
                    or decisions.get(title)
                )

                # Find match in profile
                matched_proj = None
                for ep in existing_projs:
                    comp = compare_projects_multi_signal(proj_dict, ep)
                    if comp["status"] in ("same", "possible_duplicate"):
                        matched_proj = ep
                        break

                url_candidate = (
                    proj_dict.get("url")
                    or proj_dict.get("github_url")
                    or proj_dict.get("live_url")
                    or ""
                )

                if proj_decision == "discard":
                    if matched_proj:
                        career_knowledge_service.record_user_correction(
                            db=db,
                            user_id=user_id,
                            field_name="project_duplicate",
                            original_value=title,
                            corrected_value=matched_proj.title,
                            category="discard",
                        )
                    continue

                elif proj_decision == "keep_existing":
                    if matched_proj:
                        career_knowledge_service.record_user_correction(
                            db=db,
                            user_id=user_id,
                            field_name="project_duplicate",
                            original_value=title,
                            corrected_value=matched_proj.title,
                            category="keep_existing",
                        )
                    continue

                elif proj_decision == "replace_with_new":
                    target = matched_proj or next(
                        (p for p in existing_projs if is_same_project_title(p.title, title)),
                        None,
                    )
                    if target:
                        target.title = title
                        target.role = proj_dict.get("role") or target.role
                        target.url = url_candidate or target.url
                        target.description = proj_dict.get("description") or target.description
                        target.technologies = proj_dict.get("technologies") or target.technologies
                        target.bullets = proj_dict.get("bullets") or target.bullets
                        target.start_date = proj_dict.get("start_date") or target.start_date
                        target.end_date = proj_dict.get("end_date") or target.end_date
                        counts["projects_updated"] += 1
                        career_knowledge_service.record_user_correction(
                            db=db,
                            user_id=user_id,
                            field_name="project_duplicate",
                            original_value=target.title,
                            corrected_value=title,
                            category="replace_with_new",
                        )
                    else:
                        new_proj = Project(
                            profile_id=profile.id,
                            title=title,
                            role=proj_dict.get("role") or "",
                            description=proj_dict.get("description") or "",
                            bullets=proj_dict.get("bullets") or [],
                            technologies=proj_dict.get("technologies") or [],
                            url=url_candidate,
                            start_date=proj_dict.get("start_date") or "",
                            end_date=proj_dict.get("end_date") or "",
                        )
                        db.add(new_proj)
                        existing_projs.append(new_proj)
                        counts["projects_added"] += 1

                elif proj_decision == "save_separate":
                    new_proj = Project(
                        profile_id=profile.id,
                        title=title,
                        role=proj_dict.get("role") or "",
                        description=proj_dict.get("description") or "",
                        bullets=proj_dict.get("bullets") or [],
                        technologies=proj_dict.get("technologies") or [],
                        url=url_candidate,
                        start_date=proj_dict.get("start_date") or "",
                        end_date=proj_dict.get("end_date") or "",
                    )
                    db.add(new_proj)
                    existing_projs.append(new_proj)
                    counts["projects_added"] += 1
                    if matched_proj:
                        career_knowledge_service.record_user_correction(
                            db=db,
                            user_id=user_id,
                            field_name="project_duplicate",
                            original_value=matched_proj.title,
                            corrected_value=title,
                            category="save_separate",
                        )

                else:
                    # Default resolution when no explicit per-item consent specified
                    if matched_proj:
                        if overwrite_existing:
                            if proj_dict.get("role"):
                                matched_proj.role = proj_dict["role"]
                            if url_candidate:
                                matched_proj.url = url_candidate
                            if proj_dict.get("description"):
                                matched_proj.description = proj_dict["description"]
                            if proj_dict.get("technologies"):
                                matched_proj.technologies = proj_dict["technologies"]
                            if proj_dict.get("bullets"):
                                matched_proj.bullets = proj_dict["bullets"]
                            if proj_dict.get("start_date"):
                                matched_proj.start_date = proj_dict["start_date"]
                            if proj_dict.get("end_date"):
                                matched_proj.end_date = proj_dict["end_date"]
                            counts["projects_updated"] += 1
                    else:
                        new_proj = Project(
                            profile_id=profile.id,
                            title=title,
                            role=proj_dict.get("role") or "",
                            description=proj_dict.get("description") or "",
                            bullets=proj_dict.get("bullets") or [],
                            technologies=proj_dict.get("technologies") or [],
                            url=url_candidate,
                            start_date=proj_dict.get("start_date") or "",
                            end_date=proj_dict.get("end_date") or "",
                        )
                        db.add(new_proj)
                        existing_projs.append(new_proj)
                        counts["projects_added"] += 1

        # 4. Experience
        if "experience" in selected_sections:
            existing_exps = {
                ((e.company or "").strip().lower(), (e.title or "").strip().lower()): e
                for e in profile.experiences
            }
            incoming_exps = []
            seen_exp_keys = set()
            for exp_dict in (extracted.get("experience") or []):
                company = (exp_dict.get("company") or "").strip()
                title = (exp_dict.get("title") or "").strip()
                key = (company.lower(), title.lower())
                if key in seen_exp_keys:
                    continue
                seen_exp_keys.add(key)
                incoming_exps.append(exp_dict)

            for exp_dict in incoming_exps:
                company = (exp_dict.get("company") or "").strip()
                title = (exp_dict.get("title") or "").strip()
                key = (company.lower(), title.lower())
                match = existing_exps.get(key)
                if match:
                    if overwrite_existing:
                        if exp_dict.get("location"):
                            match.location = exp_dict["location"]
                        if exp_dict.get("start_date"):
                            match.start_date = exp_dict["start_date"]
                        if exp_dict.get("end_date"):
                            match.end_date = exp_dict["end_date"]
                        if exp_dict.get("bullets"):
                            match.bullets = exp_dict["bullets"]
                        if exp_dict.get("technologies"):
                            match.technologies = exp_dict["technologies"]
                        counts["experience_updated"] += 1
                else:
                    new_exp = Experience(
                        profile_id=profile.id,
                        company=company,
                        title=title,
                        location=exp_dict.get("location") or "",
                        description="",
                        bullets=exp_dict.get("bullets") or [],
                        technologies=exp_dict.get("technologies") or [],
                        start_date=exp_dict.get("start_date") or "",
                        end_date=exp_dict.get("end_date") or "",
                        is_current=exp_dict.get("is_current", False),
                    )
                    db.add(new_exp)
                    existing_exps[key] = new_exp
                    counts["experience_added"] += 1

        # 5. Education
        if "education" in selected_sections:
            existing_edus = {
                ((ed.institution or "").strip().lower(), (ed.degree or "").strip().lower()): ed
                for ed in profile.educations
            }
            incoming_edus = []
            seen_edu_keys = set()
            for edu_dict in (extracted.get("education") or []):
                institution = (edu_dict.get("institution") or "").strip()
                degree = (edu_dict.get("degree") or "").strip()
                key = (institution.lower(), degree.lower())
                if key in seen_edu_keys:
                    continue
                seen_edu_keys.add(key)
                incoming_edus.append(edu_dict)

            for edu_dict in incoming_edus:
                institution = (edu_dict.get("institution") or "").strip()
                degree = (edu_dict.get("degree") or "").strip()
                key = (institution.lower(), degree.lower())
                match = existing_edus.get(key)
                if match:
                    if overwrite_existing:
                        if edu_dict.get("grade"):
                            match.grade = edu_dict["grade"]
                        if edu_dict.get("start_date"):
                            match.start_date = edu_dict["start_date"]
                        if edu_dict.get("end_date"):
                            match.end_date = edu_dict["end_date"]
                        counts["education_updated"] += 1
                else:
                    new_edu = Education(
                        profile_id=profile.id,
                        institution=institution,
                        degree=degree,
                        field_of_study=edu_dict.get("field_of_study") or "",
                        grade=edu_dict.get("grade") or "",
                        start_date=edu_dict.get("start_date") or "",
                        end_date=edu_dict.get("end_date") or "",
                    )
                    db.add(new_edu)
                    existing_edus[key] = new_edu
                    counts["education_added"] += 1

        # 6. Certifications
        if "certifications" in selected_sections:
            existing_certs = {c.name.strip().lower(): c for c in profile.certifications if c.name}
            incoming_certs = []
            seen_cert_keys = set()
            for cert_dict in (extracted.get("certifications") or []):
                name = (cert_dict.get("name") or "").strip()
                if not name or name.lower() in seen_cert_keys:
                    continue
                seen_cert_keys.add(name.lower())
                incoming_certs.append(cert_dict)

            for cert_dict in incoming_certs:
                name = (cert_dict.get("name") or "").strip()
                if not name:
                    continue
                match = existing_certs.get(name.lower())
                if match:
                    if overwrite_existing:
                        if cert_dict.get("issuer"):
                            match.issuer = cert_dict["issuer"]
                        if cert_dict.get("issue_date"):
                            match.issue_date = cert_dict["issue_date"]
                        if cert_dict.get("credential_url"):
                            match.credential_url = cert_dict["credential_url"]
                        if cert_dict.get("item_type"):
                            match.item_type = cert_dict["item_type"]
                        if cert_dict.get("status_note"):
                            match.status_note = cert_dict["status_note"]
                        if cert_dict.get("expiry_date") or cert_dict.get("expiration_date"):
                            match.expiry_date = cert_dict.get("expiry_date") or cert_dict.get("expiration_date")
                        counts["certifications_updated"] += 1
                else:
                    new_cert = Certification(
                        profile_id=profile.id,
                        name=name,
                        issuer=cert_dict.get("issuer") or None,
                        item_type=cert_dict.get("item_type") or "certification",
                        status_note=cert_dict.get("status_note") or None,
                        expiry_date=cert_dict.get("expiry_date") or cert_dict.get("expiration_date") or None,
                        issue_date=cert_dict.get("issue_date") or "",
                        credential_url=cert_dict.get("credential_url") or "",
                    )
                    db.add(new_cert)
                    existing_certs[name.lower()] = new_cert
                    counts["certifications_added"] += 1

        db.commit()
        db.refresh(profile)

        return {
            "status": "success",
            "message": "Extracted resume data successfully applied to candidate profile.",
            "applied_sections": selected_sections,
            "counts": counts,
        }

    @classmethod
    def get_user_resumes(cls, db: Session, user_id: int) -> List[MasterResume]:
        return db.query(MasterResume).filter(MasterResume.user_id == user_id).all()

    @classmethod
    def delete_resume(cls, db: Session, user_id: int, resume_id: int) -> bool:
        resume = db.query(MasterResume).filter(
            MasterResume.id == resume_id, MasterResume.user_id == user_id
        ).first()
        if not resume:
            return False
        storage_service.delete_file(resume.file_path)
        db.delete(resume)
        db.commit()
        return True


profile_service = ProfileService()
