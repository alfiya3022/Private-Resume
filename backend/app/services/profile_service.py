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
)
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

        # 2. Extract plain text with PyMuPDF
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
            # Clean up old stored PDF file if path differs
            if existing_resume.file_path and existing_resume.file_path != file_path:
                storage_service.delete_file(existing_resume.file_path)

            existing_resume.filename = file.filename
            existing_resume.file_path = file_path
            existing_resume.file_size = file_size
            existing_resume.raw_text = raw_text
            existing_resume.extracted_data = extracted_data
            existing_resume.is_active = True
            db.commit()
            db.refresh(existing_resume)
            resume = existing_resume
        else:
            # 3. Create MasterResume record
            resume = MasterResume(
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                raw_text=raw_text,
                extracted_data=extracted_data,
                is_active=True,
            )
            db.add(resume)
            db.commit()
            db.refresh(resume)

        # 4. Extract skills and populate profile if empty
        profile = cls.get_or_create_profile(db, user_id)
        existing_skills = {s.name.lower() for s in profile.skills}
        extracted_skills = extracted_data.get("skills") or []
        for item in extracted_skills:
            if isinstance(item, dict):
                skill_name = item.get("name")
                skill_cat = item.get("category") or "Technical"
            else:
                skill_name = str(item)
                skill_cat = "Technical"
            if skill_name and skill_name.lower() not in existing_skills:
                new_skill = CandidateSkill(
                    profile_id=profile.id,
                    name=skill_name,
                    category=skill_cat,
                    proficiency="Intermediate",
                )
                db.add(new_skill)
                existing_skills.add(skill_name.lower())
        db.commit()
        db.refresh(profile)

        return resume

    @classmethod
    def compare_extracted_data_with_profile(
        cls, profile: CandidateProfile, extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compares extracted resume data against current profile and generates diff/conflict report."""
        if not extracted_data:
            return {}

        extracted_p = extracted_data.get("personal_info") or {}
        personal_diff = {}
        for field in ["phone", "location", "linkedin_url", "github_url", "portfolio_url"]:
            curr = getattr(profile, field, "") or ""
            extr = extracted_p.get(field) or ""
            if not curr and extr:
                s_code = "new"
            elif curr and extr and curr.strip().lower() != extr.strip().lower():
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

        existing_skill_names = {s.name.lower() for s in profile.skills}
        extracted_skills = extracted_data.get("skills") or []
        new_skills = []
        matching_skills = []
        for s in extracted_skills:
            s_name = s.get("name", "") if isinstance(s, dict) else str(s)
            if not s_name:
                continue
            if s_name.lower() in existing_skill_names:
                matching_skills.append(s)
            else:
                new_skills.append(s)
        skills_diff = {
            "new_skills": new_skills,
            "matching_skills": matching_skills,
            "total_extracted": len(extracted_skills),
        }

        extracted_projs = extracted_data.get("projects") or []
        deduped_extracted_projs = []
        for p in extracted_projs:
            t = (p.get("title") or "").strip()
            if t and not any(is_same_project_title(t, prev.get("title") or "") for prev in deduped_extracted_projs):
                deduped_extracted_projs.append(p)

        def matches_existing_project(p_dict):
            t = (p_dict.get("title") or "").strip()
            return any(is_same_project_title(t, ep.title or "") for ep in profile.projects)

        projects_diff = {
            "new_items": [p for p in deduped_extracted_projs if not matches_existing_project(p)],
            "matching_items": [p for p in deduped_extracted_projs if matches_existing_project(p)],
            "total_extracted": len(deduped_extracted_projs),
        }

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
        comparison = cls.compare_extracted_data_with_profile(profile, extracted)

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
    ) -> Dict[str, Any]:
        """Selectively applies approved extracted sections to candidate profile without destructive overwriting."""
        profile = cls.get_or_create_profile(db, user_id)
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
            if extracted.get("summary") and (overwrite_existing or not profile.summary):
                profile.summary = extracted["summary"]
                counts["personal_fields_updated"] += 1

        # 2. Skills
        if "skills" in selected_sections:
            existing_skill_names = {s.name.lower() for s in profile.skills}
            for item in (extracted.get("skills") or []):
                if isinstance(item, dict):
                    skill_name = item.get("name")
                    skill_cat = item.get("category") or "Technical"
                else:
                    skill_name = str(item)
                    skill_cat = "Technical"
                if skill_name and skill_name.lower() not in existing_skill_names:
                    db.add(
                        CandidateSkill(
                            profile_id=profile.id,
                            name=skill_name,
                            category=skill_cat,
                            proficiency="Intermediate",
                        )
                    )
                    existing_skill_names.add(skill_name.lower())
                    counts["skills_added"] += 1

        # 3. Projects
        if "projects" in selected_sections:
            existing_projs = [p for p in profile.projects if p.title]

            # Deduplicate incoming projects within the same incoming list
            incoming_projs = []
            for proj_dict in (extracted.get("projects") or []):
                title = (proj_dict.get("title") or "").strip()
                if not title:
                    continue
                if any(is_same_project_title(title, seen.get("title") or "") for seen in incoming_projs):
                    continue
                incoming_projs.append(proj_dict)

            for proj_dict in incoming_projs:
                title = (proj_dict.get("title") or "").strip()
                if not title:
                    continue
                # Match incoming project by normalized title / SequenceMatcher >= 0.9
                match = next((p for p in existing_projs if is_same_project_title(p.title, title)), None)
                url_candidate = proj_dict.get("url") or proj_dict.get("github_url") or proj_dict.get("live_url") or ""
                if match:
                    if overwrite_existing:
                        if url_candidate:
                            match.url = url_candidate
                        if proj_dict.get("technologies"):
                            match.technologies = proj_dict["technologies"]
                        if proj_dict.get("bullets"):
                            match.bullets = proj_dict["bullets"]
                        if proj_dict.get("start_date"):
                            match.start_date = proj_dict["start_date"]
                        if proj_dict.get("end_date"):
                            match.end_date = proj_dict["end_date"]
                        counts["projects_updated"] += 1
                else:
                    new_proj = Project(
                        profile_id=profile.id,
                        title=title,
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
                        counts["experience_updated"] += 1
                else:
                    new_exp = Experience(
                        profile_id=profile.id,
                        company=company,
                        title=title,
                        location=exp_dict.get("location") or "",
                        description="",
                        bullets=exp_dict.get("bullets") or [],
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
                        counts["certifications_updated"] += 1
                else:
                    new_cert = Certification(
                        profile_id=profile.id,
                        name=name,
                        issuer=cert_dict.get("issuer") or "",
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
