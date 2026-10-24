import logging

import re
from pathlib import Path
from typing import Dict, Any

import pymupdf
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.tailored_resume import TailoredResume
from app.models.profile import CandidateProfile, CandidateSkill
from app.models.artifact import ResumeArtifact
from app.models.validation import ResumeValidation

logger = logging.getLogger(__name__)


PLACEHOLDER_PATTERNS = [
    r"\[(?:Your Name|Company(?: Name)?|Title|Job Title|City,\s*State|Email|Phone|Insert\s+[^\]]+)\]",
    r"\{\{[A-Za-z0-9_]+\}\}",
    r"<<[A-Za-z0-9_]+>>",
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bLorem ipsum\b",
    r"\bXXXX\b",
    r"\bYYYY\b",
]

CORE_HEADINGS = [
    ("Summary", [r"summary", r"professional summary", r"executive summary", r"about me", r"objective"]),
    ("Experience", [r"experience", r"professional experience", r"employment", r"work history", r"technical experience"]),
    ("Skills", [r"skills", r"technical competencies", r"technical skills", r"technologies"]),
    ("Education", [r"education", r"academic background", r"qualifications"]),
]

EMAIL_PATTERN = r"[\w.+-]+@[\w.-]+\.\w+"

# Supports common Indian mobile numbers with optional +91/91/0091 prefix.
INDIAN_PHONE_PATTERN = (
    r"(?<!\d)(?:(?:\+?91|0091)[\s().-]?)?"
    r"(?:0[\s().-]?)?[6-9]\d{4}[\s.-]?\d{5}(?!\d)"
)

# Retain support for common US-style phone numbers.
US_PHONE_PATTERN = r"(?<!\d)\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)"


class ValidationService:
    def validate_resume(self, db: Session, user: User, resume_id: int) -> ResumeValidation:
        """Run objective pre-flight checks on the compiled PDF and resume content."""

        resume = db.query(TailoredResume).filter(
            TailoredResume.id == resume_id,
            TailoredResume.user_id == user.id,
        ).first()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tailored resume not found or access unauthorized",
            )

        pdf_artifact = db.query(ResumeArtifact).filter(
            ResumeArtifact.tailored_resume_id == resume.id,
            ResumeArtifact.user_id == user.id,
            ResumeArtifact.artifact_type == "pdf",
        ).first()

        if not pdf_artifact or not Path(pdf_artifact.file_path).is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Compiled PDF not found. Please compile the resume in Stage 5 before running validation.",
            )

        pdf_path = Path(pdf_artifact.file_path)
        checks: Dict[str, Any] = {}
        full_text = ""
        doc = None
        pdf_error = None
        text_error = None

        # 1. PDF Generation & Health Check
        try:
            doc = pymupdf.open(str(pdf_path))
            page_count = len(doc)
            file_size = pdf_path.stat().st_size

            if page_count > 0 and file_size > 500:
                checks["pdf_generation"] = {
                    "name": "pdf_generation",
                    "status": "PASS",
                    "title": "PDF Document Health",
                    "message": (
                        f"Valid document structure ({page_count} page"
                        f"{'s' if page_count > 1 else ''}, "
                        f"{round(file_size / 1024, 1)} KB)."
                    ),
                    "details": {"pages": page_count, "size_bytes": file_size},
                }
            else:
                checks["pdf_generation"] = {
                    "name": "pdf_generation",
                    "status": "FAIL",
                    "title": "PDF Document Health",
                    "message": "Generated PDF is empty or has no pages.",
                }

            # 2. Text Extraction
            try:
                full_text = "\n".join(page.get_text() for page in doc)
            except Exception as exc:
                logger.error("Failed to extract text from PDF: %s", exc)
                text_error = "Unable to extract text from PDF." 

        except Exception as exc:
            logger.error("Failed to inspect PDF: %s", exc)
            pdf_error = "Unable to open or inspect PDF document structure."
            checks["pdf_generation"] = {
                "name": "pdf_generation",
                "status": "FAIL",
                "title": "PDF Document Health",
                "message": pdf_error,
            }
        finally:
            if doc is not None:
                doc.close()

        # 2. Text Extractability Check
        text_len = len(full_text.strip())

        if pdf_error or text_error:
            checks["text_extractability"] = {
                "name": "text_extractability",
                "status": "FAIL",
                "title": "ATS Text Extractability",
                "message": "Unable to extract text from the PDF.",
                "details": {"character_count": text_len},
            }
        elif text_len > 150:
            checks["text_extractability"] = {
                "name": "text_extractability",
                "status": "PASS",
                "title": "ATS Text Extractability",
                "message": (
                    f"Extractable text detected ({text_len} characters). "
                    "This check does not guarantee correct ATS parsing."
                ),
                "details": {"character_count": text_len},
            }
        else:
            checks["text_extractability"] = {
                "name": "text_extractability",
                "status": "FAIL",
                "title": "ATS Text Extractability",
                "message": (
                    "Extractable text is below the configured threshold. "
                    "Review whether the PDF contains selectable text."
                ),
                "details": {"character_count": text_len},
            }

        text_lower = full_text.lower()

        # 3. Contact Details Detection
        email_match = re.search(EMAIL_PATTERN, full_text, re.IGNORECASE)
        phone_match = re.search(
            f"(?:{INDIAN_PHONE_PATTERN})|(?:{US_PHONE_PATTERN})",
            full_text,
        )

        name_found = False
        if user.full_name and user.full_name.strip():
            name_pattern = r"\s+".join(
                re.escape(part) for part in user.full_name.split()
            )
            name_found = bool(re.search(name_pattern, full_text, re.IGNORECASE))

        missing_contacts = []
        if not name_found:
            missing_contacts.append("Name")
        if not email_match:
            missing_contacts.append("Email")
        if not phone_match:
            missing_contacts.append("Phone")

        if not missing_contacts:
            checks["contact_details"] = {
                "name": "contact_details",
                "status": "PASS",
                "title": "Contact Information",
                "message": "Candidate name, email, and phone number were detected.",
                "details": {
                    "name_found": name_found,
                    "email": email_match.group(0),
                    "phone": phone_match.group(0),
                },
            }
        elif missing_contacts == ["Phone"]:
            checks["contact_details"] = {
                "name": "contact_details",
                "status": "WARN",
                "title": "Contact Information",
                "message": "Candidate name and email were detected, but a phone number was not found.",
                "details": {"missing": missing_contacts, "name_found": name_found},
            }
        else:
            checks["contact_details"] = {
                "name": "contact_details",
                "status": "FAIL",
                "title": "Contact Information",
                "message": f"Missing critical contact information: {', '.join(missing_contacts)}.",
                "details": {"missing": missing_contacts, "name_found": name_found},
            }

        # 4. Standard Section Headings Recognition
        found_headings = []
        missing_headings = []

        for section_name, patterns in CORE_HEADINGS:
            matched = any(
                re.search(rf"\b{pat}\b", text_lower)
                for pat in patterns
            )
            if not matched and section_name == "Summary":
                summary_text = (resume.content or {}).get("summary", "").strip().lower()
                if summary_text and summary_text[:30] in text_lower:
                    matched = True
            if matched:
                found_headings.append(section_name)
            else:
                missing_headings.append(section_name)

        if not missing_headings:
            checks["standard_headings"] = {
                "name": "standard_headings",
                "status": "PASS",
                "title": "Standard ATS Headings",
                "message": f"All 4 core ATS headings were recognized ({', '.join(found_headings)}).",
                "details": {"found": found_headings},
            }
        else:
            checks["standard_headings"] = {
                "name": "standard_headings",
                "status": "WARN" if len(missing_headings) <= 1 else "FAIL",
                "title": "Standard ATS Headings",
                "message": f"Missing standard section headings: {', '.join(missing_headings)}.",
                "details": {
                    "missing": missing_headings,
                    "found": found_headings,
                },
            }

        # 5. Placeholder & Template Artifact Detection
        placeholders_found = []

        for pattern in PLACEHOLDER_PATTERNS:
            placeholders_found.extend(
                re.findall(pattern, full_text, flags=re.IGNORECASE)
            )

        if not placeholders_found:
            checks["placeholders"] = {
                "name": "placeholders",
                "status": "PASS",
                "title": "Template Placeholder Audit",
                "message": "No recognized template placeholders were detected.",
            }
        else:
            unique_tokens = list(set(placeholders_found))
            checks["placeholders"] = {
                "name": "placeholders",
                "status": "FAIL",
                "title": "Template Placeholder Audit",
                "message": (
                    "Unresolved placeholder tokens detected: "
                    f"{', '.join(unique_tokens[:5])}."
                ),
                "details": {"tokens": unique_tokens},
            }

        # 6. Candidate Evidence Grounding
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == user.id
        ).first()

        verified_skills = []
        if profile:
            skills = db.query(CandidateSkill).filter(
                CandidateSkill.profile_id == profile.id
            ).all()
            verified_skills = [skill.name for skill in skills]

        checks["integrity_audit"] = {
            "name": "integrity_audit",
            "status": "WARN",
            "title": "Candidate Evidence Grounding",
            "message": (
                "Automated claim-to-evidence verification is not implemented. "
                "Candidate skills were loaded, but resume claims were not "
                "verified against profile evidence."
            ),
            "details": {
                "verified_skill_count": len(verified_skills),
                "verification_performed": False,
            },
        }

        # Compute Overall Status and a score based on individual check results.
        statuses = [item["status"] for item in checks.values()]

        if "FAIL" in statuses:
            overall_status = "FAIL"
        elif "WARN" in statuses:
            overall_status = "WARN"
        else:
            overall_status = "PASS"

        status_points = {"PASS": 100, "WARN": 50, "FAIL": 0}
        score = round(
            sum(status_points.get(item["status"], 0) for item in checks.values())
            / len(checks)
        ) if checks else 0

        # Save or update validation record.
        validation = db.query(ResumeValidation).filter(
            ResumeValidation.tailored_resume_id == resume.id,
            ResumeValidation.user_id == user.id,
        ).first()

        if not validation:
            validation = ResumeValidation(
                tailored_resume_id=resume.id,
                user_id=user.id,
                overall_status=overall_status,
                score=score,
                checks=checks,
            )
            db.add(validation)
        else:
            validation.overall_status = overall_status
            validation.score = score
            validation.checks = checks

        db.commit()
        db.refresh(validation)
        return validation

    def get_validation(
        self,
        db: Session,
        user: User,
        resume_id: int,
    ) -> ResumeValidation:
        """Retrieve the existing validation report for a resume version."""

        validation = db.query(ResumeValidation).filter(
            ResumeValidation.tailored_resume_id == resume_id,
            ResumeValidation.user_id == user.id,
        ).first()

        if not validation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation report not found. Run validation first.",
            )

        return validation


validation_service = ValidationService()
