from datetime import datetime
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.job import Job
from app.models.analysis import JobRequirement
from app.models.match import MatchAnalysis
from app.services.profile_service import profile_service
from app.services.analysis_service import analysis_service


class MatchingService:
    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().lower()

    @staticmethod
    def _parse_month_year(date_str: Optional[str]) -> Tuple[Optional[int], int]:
        if not date_str:
            return None, 1
        date_str = date_str.strip()
        y_match = re.search(r"\b(19\d\d|20\d\d)\b", date_str)
        if not y_match:
            return None, 1
        year = int(y_match.group(1))

        m_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        month = 1
        for m_name, m_num in m_map.items():
            if m_name in date_str.lower():
                month = m_num
                break
        return year, month

    @classmethod
    def calculate_candidate_experience_years(cls, profile) -> float:
        """Estimates candidate total years of experience from profile experiences."""
        if not profile or not getattr(profile, "experiences", None):
            return 0.0

        total_months = 0
        now = datetime.now()
        for exp in profile.experiences:
            s_year, s_month = cls._parse_month_year(exp.start_date)
            if not s_year:
                continue
            if exp.is_current or not exp.end_date or "present" in (exp.end_date or "").lower():
                e_year, e_month = now.year, now.month
            else:
                e_year, e_month = cls._parse_month_year(exp.end_date)
                if not e_year:
                    e_year, e_month = s_year, s_month + 12

            months = (e_year - s_year) * 12 + (e_month - s_month)
            if months > 0:
                total_months += months

        return round(total_months / 12.0, 1)

    @classmethod
    def check_experience_qualification(cls, profile, job_req: JobRequirement) -> Dict[str, Any]:
        """Compares candidate total experience against required min_years.
        Treats min_years as the requirement (0 years matches '0 to 2 years' job).
        """
        min_years = None
        if job_req.raw_analysis and isinstance(job_req.raw_analysis, dict):
            min_years = job_req.raw_analysis.get("min_years")
        if min_years is None and job_req.experience_years:
            try:
                min_years = int(re.search(r"\d+", job_req.experience_years).group(0))
            except Exception:
                min_years = None

        candidate_years = cls.calculate_candidate_experience_years(profile)
        is_qualified = True
        if min_years is not None:
            is_qualified = (candidate_years >= min_years)

        return {
            "required_min_years": min_years,
            "candidate_years": candidate_years,
            "is_qualified": is_qualified,
        }

    @classmethod
    def calculate_match(
        cls, db: Session, user_id: int, job_id: int
    ) -> MatchAnalysis:
        """Executes deterministic resume-to-job matching based on structured candidate evidence."""
        profile = profile_service.get_or_create_profile(db, user_id)
        job_req = db.query(JobRequirement).filter(JobRequirement.job_id == job_id).first()

        if not job_req:
            # Trigger analysis first if not already present
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job must be analyzed before running matching. Trigger /analyze first.",
            )

        # 1. Index candidate evidence
        candidate_skills_map: Dict[str, str] = {
            cls._normalize(s.name): s.name for s in profile.skills
        }

        # Index project evidence
        project_evidence: Dict[str, List[str]] = {}
        for proj in profile.projects:
            proj_text = f"{proj.title} {' '.join(proj.technologies or [])} {' '.join(proj.bullets or [])}".lower()
            for skill_norm, original_name in candidate_skills_map.items():
                if skill_norm in proj_text:
                    if skill_norm not in project_evidence:
                        project_evidence[skill_norm] = []
                    project_evidence[skill_norm].append(f"Project: {proj.title}")

        # Index experience evidence
        exp_evidence: Dict[str, List[str]] = {}
        for exp in profile.experiences:
            exp_text = f"{exp.company} {exp.title} {' '.join(exp.bullets or [])}".lower()
            for skill_norm, original_name in candidate_skills_map.items():
                if skill_norm in exp_text:
                    if skill_norm not in exp_evidence:
                        exp_evidence[skill_norm] = []
                    exp_evidence[skill_norm].append(f"Experience: {exp.company} ({exp.title})")

        # 2. Extract job skills
        job_required: Set[str] = {
            cls._normalize(s) for s in (job_req.required_skills or [])
        }
        # Include core languages, frameworks, databases into required if not specified
        for group in [job_req.languages, job_req.frameworks, job_req.databases]:
            for item in group or []:
                job_required.add(cls._normalize(item))

        job_preferred: Set[str] = {
            cls._normalize(s) for s in (job_req.preferred_skills or [])
        }
        for group in [job_req.cloud, job_req.tools]:
            for item in group or []:
                if cls._normalize(item) not in job_required:
                    job_preferred.add(cls._normalize(item))

        # 3. Categorize into the 4 locked classes
        matched_skills: List[str] = []
        weak_skills: List[str] = []
        missing_skills: List[str] = []
        evidence_map: Dict[str, List[str]] = {}

        all_target_skills = list(job_required.union(job_preferred))

        for skill_norm in all_target_skills:
            # Check candidate profile presence
            is_in_profile = skill_norm in candidate_skills_map
            has_proj_evidence = skill_norm in project_evidence
            has_exp_evidence = skill_norm in exp_evidence

            # Format name nicely
            display_name = candidate_skills_map.get(skill_norm, skill_norm.title())

            if is_in_profile and (has_proj_evidence or has_exp_evidence):
                # Strong match backed by project or experience
                matched_skills.append(display_name)
                sources = project_evidence.get(skill_norm, []) + exp_evidence.get(skill_norm, [])
                evidence_map[display_name] = sources
            elif is_in_profile:
                # In profile but without specific project/experience evidence
                weak_skills.append(display_name)
                evidence_map[display_name] = ["Profile Skills (General listing, lacks dedicated project/job evidence)"]
            elif has_proj_evidence or has_exp_evidence:
                # Mentioned in project but missing from primary skills list
                weak_skills.append(display_name)
                evidence_map[display_name] = project_evidence.get(skill_norm, []) + exp_evidence.get(skill_norm, [])
            else:
                # Completely absent from candidate data
                missing_skills.append(display_name)

        # Unsupported claims: Any skill in candidate profile that has 0 projects, 0 experiences,
        # but is claimed at advanced/expert level without verification
        unsupported_claims: List[str] = []
        for s in profile.skills:
            s_norm = cls._normalize(s.name)
            if s.proficiency == "Expert" and s_norm not in project_evidence and s_norm not in exp_evidence:
                unsupported_claims.append(f"{s.name} (Claimed as Expert but has no linked projects or work evidence)")

        # Verify experience requirement qualification (min_years treated as requirement)
        exp_qualification = cls.check_experience_qualification(profile, job_req)
        if exp_qualification["required_min_years"] is not None and not exp_qualification["is_qualified"]:
            unsupported_claims.append(
                f"Experience: Role requires minimum {exp_qualification['required_min_years']} years (profile has {exp_qualification['candidate_years']:.1f} years)"
            )

        # 4. Compute Estimated Job Match Score
        # 70% weight on required skills, 30% on preferred skills
        def calculate_category_score(skill_set: Set[str]) -> float:
            if not skill_set:
                return 1.0  # If no requirements in category, give full credit
            points = 0.0
            for sk in skill_set:
                disp = candidate_skills_map.get(sk, sk.title())
                if disp in matched_skills:
                    points += 1.0
                elif disp in weak_skills:
                    points += 0.5
            return points / len(skill_set)

        req_ratio = calculate_category_score(job_required)
        pref_ratio = calculate_category_score(job_preferred)

        total_match_score = int(round((req_ratio * 70.0) + (pref_ratio * 30.0)))
        total_match_score = max(0, min(100, total_match_score))

        # 5. Persist MatchAnalysis record
        match_record = db.query(MatchAnalysis).filter(MatchAnalysis.job_id == job_id).first()
        if not match_record:
            match_record = MatchAnalysis(
                job_id=job_id,
                user_id=user_id,
                estimated_match_score=total_match_score,
                matched_skills=sorted(matched_skills),
                weak_skills=sorted(weak_skills),
                missing_skills=sorted(missing_skills),
                unsupported_claims=sorted(unsupported_claims),
                evidence_map=evidence_map,
            )
            db.add(match_record)
        else:
            match_record.estimated_match_score = total_match_score
            match_record.matched_skills = sorted(matched_skills)
            match_record.weak_skills = sorted(weak_skills)
            match_record.missing_skills = sorted(missing_skills)
            match_record.unsupported_claims = sorted(unsupported_claims)
            match_record.evidence_map = evidence_map

        db.commit()
        db.refresh(match_record)
        return match_record

    @staticmethod
    def get_match_by_job_id(
        db: Session, user_id: int, job_id: int
    ) -> Optional[MatchAnalysis]:
        """Retrieves existing match analysis verifying candidate ownership."""
        return db.query(MatchAnalysis).filter(
            MatchAnalysis.job_id == job_id, MatchAnalysis.user_id == user_id
        ).first()


matching_service = MatchingService()
