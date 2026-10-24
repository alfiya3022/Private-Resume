import copy
import logging
from typing import Dict, Any, Tuple, Optional, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.tailored_resume import TailoredResume
from app.models.profile import CandidateProfile
from app.models.resume import MasterResume

logger = logging.getLogger(__name__)


class ResolutionService:
    """Pre-generation resolution service.

    Deterministically recovers eligible missing metadata (e.g. LinkedIn, GitHub,
    project repository links, dates, certification credential links) before LaTeX
    rendering or validation.

    Strict source precedence:
      1. User-approved value in Tailored Resume (content dict)
      2. Current reviewed CandidateProfile value
      3. Preserved Master Resume extraction (MasterResume.extracted_data)
      4. None

    CRITICAL INTEGRITY RULES:
      - Does NOT mutate the saved database TailoredResume record.
      - NEVER restores intentionally cleared fields or excluded items.
      - NEVER re-injects omitted projects, experiences, certifications, or bullet points.
      - Only enriches existing, included items with missing metadata fields.
    """

    @classmethod
    def resolve_effective_content(
        cls,
        db: Session,
        user: User,
        resume: TailoredResume,
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Resolves effective content and tracks provenance of each recovered field.

        Returns:
            Tuple of (effective_content, provenance_dict)
            where provenance maps field paths to "tailored_resume", "profile", or "master_resume".
        """
        raw_content = resume.content or {}
        effective: Dict[str, Any] = copy.deepcopy(raw_content)
        provenance: Dict[str, str] = {}

        # 1. Fetch reviewed profile
        profile: Optional[CandidateProfile] = (
            db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        )

        # 2. Fetch active/latest master resume with extracted data
        master_resume: Optional[MasterResume] = (
            db.query(MasterResume)
            .filter(MasterResume.user_id == user.id, MasterResume.is_active == True)
            .order_by(MasterResume.id.desc())
            .first()
        )
        extracted: Dict[str, Any] = (
            master_resume.extracted_data if master_resume and master_resume.extracted_data else {}
        )
        extracted_personal = extracted.get("personal_info") or {}

        # --- A. CONTACT INFO RESOLUTION ---
        contact = effective.setdefault("contact_info", {})

        def resolve_field(field_key: str, profile_val: Optional[str], master_val: Optional[str]):
            current_val = (contact.get(field_key) or "").strip()
            if current_val:
                provenance[f"contact.{field_key}"] = "tailored_resume"
                return

            # Check profile
            if profile_val and str(profile_val).strip():
                contact[field_key] = str(profile_val).strip()
                provenance[f"contact.{field_key}"] = "profile"
                return

            # Check master resume
            if master_val and str(master_val).strip():
                contact[field_key] = str(master_val).strip()
                provenance[f"contact.{field_key}"] = "master_resume"
                return

        # Phone
        resolve_field(
            "phone",
            profile.phone if profile else None,
            extracted_personal.get("phone"),
        )

        # Location
        resolve_field(
            "location",
            profile.location if profile else None,
            extracted_personal.get("location"),
        )

        # LinkedIn
        # Accept both linkedin and linkedin_url keys
        current_li = (contact.get("linkedin") or contact.get("linkedin_url") or "").strip()
        if current_li:
            contact["linkedin"] = current_li
            contact["linkedin_url"] = current_li
            provenance["contact.linkedin"] = "tailored_resume"
        else:
            p_li = (profile.linkedin_url if profile else "") or ""
            m_li = (extracted_personal.get("linkedin_url") or "")
            if p_li.strip():
                contact["linkedin"] = p_li.strip()
                contact["linkedin_url"] = p_li.strip()
                provenance["contact.linkedin"] = "profile"
            elif m_li.strip():
                contact["linkedin"] = m_li.strip()
                contact["linkedin_url"] = m_li.strip()
                provenance["contact.linkedin"] = "master_resume"

        # GitHub
        current_gh = (contact.get("github") or contact.get("github_url") or "").strip()
        if current_gh:
            contact["github"] = current_gh
            contact["github_url"] = current_gh
            provenance["contact.github"] = "tailored_resume"
        else:
            p_gh = (profile.github_url if profile else "") or ""
            m_gh = (extracted_personal.get("github_url") or "")
            if p_gh.strip():
                contact["github"] = p_gh.strip()
                contact["github_url"] = p_gh.strip()
                provenance["contact.github"] = "profile"
            elif m_gh.strip():
                contact["github"] = m_gh.strip()
                contact["github_url"] = m_gh.strip()
                provenance["contact.github"] = "master_resume"

        # Portfolio
        current_port = (contact.get("portfolio") or contact.get("portfolio_url") or "").strip()
        if current_port:
            contact["portfolio"] = current_port
            contact["portfolio_url"] = current_port
            provenance["contact.portfolio"] = "tailored_resume"
        else:
            p_port = (profile.portfolio_url if profile else "") or ""
            m_port = (extracted_personal.get("portfolio_url") or "")
            if p_port.strip():
                contact["portfolio"] = p_port.strip()
                contact["portfolio_url"] = p_port.strip()
                provenance["contact.portfolio"] = "profile"
            elif m_port.strip():
                contact["portfolio"] = m_port.strip()
                contact["portfolio_url"] = m_port.strip()
                provenance["contact.portfolio"] = "master_resume"

        # --- B. PROJECTS METADATA RECOVERY ---
        # Note: ONLY enrich included projects; NEVER add projects omitted by tailoring/user.
        profile_projects = profile.projects if profile else []
        extracted_projects = extracted.get("projects") or []

        projects_list = effective.get("projects", [])
        if isinstance(projects_list, list):
            for i, proj in enumerate(projects_list):
                if not isinstance(proj, dict):
                    continue
                p_title = (proj.get("name") or proj.get("title") or "").strip().lower()
                if not p_title:
                    continue

                # Find match in profile
                matched_p_prof = next(
                    (p for p in profile_projects if (p.title or "").strip().lower() == p_title),
                    None,
                )
                # Find match in master resume
                matched_p_master = next(
                    (p for p in extracted_projects if (p.get("title") or "").strip().lower() == p_title),
                    None,
                )

                # Recover github_url
                curr_gh = (proj.get("github_url") or "").strip()
                if not curr_gh:
                    if matched_p_prof and getattr(matched_p_prof, "url", None) and "github.com" in getattr(matched_p_prof, "url", "").lower():
                        proj["github_url"] = matched_p_prof.url.strip()
                        provenance[f"project.{i}.github_url"] = "profile"
                    elif matched_p_master and matched_p_master.get("github_url"):
                        proj["github_url"] = matched_p_master["github_url"].strip()
                        provenance[f"project.{i}.github_url"] = "master_resume"

                # Recover live_url / link
                curr_live = (proj.get("live_url") or proj.get("link") or proj.get("url") or "").strip()
                if not curr_live:
                    if matched_p_prof and getattr(matched_p_prof, "url", None) and "github.com" not in getattr(matched_p_prof, "url", "").lower():
                        proj["live_url"] = matched_p_prof.url.strip()
                        provenance[f"project.{i}.live_url"] = "profile"
                    elif matched_p_master and matched_p_master.get("live_url"):
                        proj["live_url"] = matched_p_master["live_url"].strip()
                        provenance[f"project.{i}.live_url"] = "master_resume"

                # Recover dates
                curr_start = (proj.get("start_date") or "").strip()
                curr_end = (proj.get("end_date") or "").strip()
                if not curr_start and not curr_end and not (proj.get("date") or proj.get("dates")):
                    if matched_p_prof and (matched_p_prof.start_date or matched_p_prof.end_date):
                        proj["start_date"] = matched_p_prof.start_date or ""
                        proj["end_date"] = matched_p_prof.end_date or ""
                        provenance[f"project.{i}.dates"] = "profile"
                    elif matched_p_master and (matched_p_master.get("start_date") or matched_p_master.get("end_date") or matched_p_master.get("dates")):
                        proj["start_date"] = matched_p_master.get("start_date") or ""
                        proj["end_date"] = matched_p_master.get("end_date") or ""
                        if not proj["start_date"] and not proj["end_date"]:
                            proj["date"] = matched_p_master.get("dates") or ""
                        provenance[f"project.{i}.dates"] = "master_resume"

        # --- C. CERTIFICATIONS METADATA RECOVERY ---
        profile_certs = profile.certifications if profile else []
        extracted_certs = extracted.get("certifications") or []

        certs_list = effective.get("certifications", [])
        if isinstance(certs_list, list):
            for i, cert in enumerate(certs_list):
                if not isinstance(cert, dict):
                    continue
                c_name = (cert.get("name") or cert.get("title") or "").strip().lower()
                if not c_name:
                    continue

                matched_c_prof = next(
                    (c for c in profile_certs if (c.name or "").strip().lower() == c_name),
                    None,
                )
                matched_c_master = next(
                    (c for c in extracted_certs if (c.get("name") or "").strip().lower() == c_name),
                    None,
                )

                # Recover credential_url / certificate_url
                curr_url = (
                    cert.get("certificate_url")
                    or cert.get("credential_url")
                    or cert.get("url")
                    or cert.get("link")
                    or ""
                ).strip()

                if not curr_url:
                    if matched_c_prof and matched_c_prof.credential_url:
                        cert["certificate_url"] = matched_c_prof.credential_url.strip()
                        provenance[f"certification.{i}.url"] = "profile"
                    elif matched_c_master and matched_c_master.get("credential_url"):
                        cert["certificate_url"] = matched_c_master["credential_url"].strip()
                        provenance[f"certification.{i}.url"] = "master_resume"

                # Recover issuer
                curr_issuer = (cert.get("issuer") or cert.get("organization") or "").strip()
                if not curr_issuer:
                    if matched_c_prof and matched_c_prof.issuer:
                        cert["issuer"] = matched_c_prof.issuer.strip()
                        provenance[f"certification.{i}.issuer"] = "profile"
                    elif matched_c_master and matched_c_master.get("issuer"):
                        cert["issuer"] = matched_c_master["issuer"].strip()
                        provenance[f"certification.{i}.issuer"] = "master_resume"

        # --- D. EDUCATION METADATA RECOVERY ---
        profile_edus = profile.educations if profile else []
        extracted_edus = extracted.get("education") or []

        edu_list = effective.get("education", [])
        if isinstance(edu_list, list):
            for i, edu in enumerate(edu_list):
                if not isinstance(edu, dict):
                    continue
                e_inst = (edu.get("institution") or edu.get("college") or "").strip().lower()
                e_deg = (edu.get("degree") or "").strip().lower()

                matched_e_prof = next(
                    (
                        e for e in profile_edus
                        if (e_inst and (e.institution or "").strip().lower() == e_inst)
                        or (e_deg and (e.degree or "").strip().lower() == e_deg)
                    ),
                    None,
                )
                matched_e_master = next(
                    (
                        e for e in extracted_edus
                        if (e_inst and (e.get("institution") or "").strip().lower() == e_inst)
                        or (e_deg and (e.get("degree") or "").strip().lower() == e_deg)
                    ),
                    None,
                )

                # Recover institution/college if missing
                if not (edu.get("institution") or edu.get("college")):
                    if matched_e_prof and matched_e_prof.institution:
                        edu["institution"] = matched_e_prof.institution.strip()
                        provenance[f"education.{i}.institution"] = "profile"
                    elif matched_e_master and matched_e_master.get("institution"):
                        edu["institution"] = matched_e_master["institution"].strip()
                        provenance[f"education.{i}.institution"] = "master_resume"

                # Recover grade/gpa if missing
                if not (edu.get("gpa") or edu.get("grade") or edu.get("cgpa")):
                    if matched_e_prof and matched_e_prof.grade:
                        edu["gpa"] = matched_e_prof.grade.strip()
                        provenance[f"education.{i}.grade"] = "profile"
                    elif matched_e_master and matched_e_master.get("grade"):
                        edu["gpa"] = matched_e_master["grade"].strip()
                        provenance[f"education.{i}.grade"] = "master_resume"

        return effective, provenance


resolution_service = ResolutionService()
