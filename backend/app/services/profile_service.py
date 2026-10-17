from typing import List, Optional
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

    # Master Resume workflows
    @classmethod
    async def process_master_resume_upload(
        cls, db: Session, user_id: int, file: UploadFile
    ) -> MasterResume:
        # 1. Save file locally
        file_path, file_size = await storage_service.save_resume_file(user_id, file)

        # 2. Extract plain text with PyMuPDF
        try:
            raw_text = pdf_service.extract_text_from_pdf(file_path)
        except Exception as e:
            storage_service.delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not parse text from uploaded PDF: {str(e)}",
            )

        # 3. Create MasterResume record
        resume = MasterResume(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            raw_text=raw_text,
            is_active=True,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        # 4. Extract skills deterministically and populate profile if empty
        profile = cls.get_or_create_profile(db, user_id)
        detected_skills = pdf_service.detect_skills_deterministically(raw_text)
        existing_skills = {s.name.lower() for s in profile.skills}
        for skill_name in detected_skills:
            if skill_name.lower() not in existing_skills:
                new_skill = CandidateSkill(
                    profile_id=profile.id,
                    name=skill_name,
                    category="Technical",
                    proficiency="Intermediate",
                )
                db.add(new_skill)
        db.commit()
        db.refresh(profile)

        return resume

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
