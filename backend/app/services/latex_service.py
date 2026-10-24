import logging
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from io import BytesIO
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.user import User
from app.models.tailored_resume import TailoredResume
from app.models.profile import CandidateProfile
from app.models.artifact import ResumeArtifact
from app.models.validation import ResumeValidation

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "default"


def latex_escape(text: Optional[str]) -> str:
    """Escapes LaTeX special characters to ensure syntax safety and prevent injection."""
    if not text:
        return ""
    text = str(text)
    # Map special characters
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for char, replacement in replacements:
        text = text.replace(char, replacement)
    return text


class LatexService:
    def get_user_artifact_dir(self, user_id: int) -> Path:
        """Ensures isolated artifact directory for target user."""
        storage_base = Path(settings.STORAGE_DIR) / "artifacts" / str(user_id)
        storage_base.mkdir(parents=True, exist_ok=True)
        return storage_base

    def get_user_template_dir(self, user_id: int) -> Path:
        """Ensures isolated custom template directory for target user."""
        tpl_dir = Path(settings.STORAGE_DIR) / "templates" / str(user_id)
        tpl_dir.mkdir(parents=True, exist_ok=True)
        return tpl_dir

    def get_custom_template_path(self, user_id: Optional[int]) -> Optional[Path]:
        """Returns path to user's custom template main.tex if present."""
        if not user_id:
            return None
        tpl_dir = Path(settings.STORAGE_DIR) / "templates" / str(user_id)
        main_tex = tpl_dir / "main.tex"
        if main_tex.exists() and main_tex.stat().st_size > 0:
            return main_tex
        return None

    def save_user_template(self, user_id: int, filename: str, content: bytes) -> Dict[str, Any]:
        """Safely installs a user-provided LaTeX template (.tex or .zip)."""
        max_upload_bytes = 10 * 1024 * 1024
        max_extracted_bytes = 25 * 1024 * 1024
        max_archive_files = 100

        if not filename or not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A non-empty .tex or .zip template is required.",
            )
        if len(content) > max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Template uploads must be 10 MB or smaller.",
            )

        lower_name = Path(filename).name.lower()
        if not (lower_name.endswith(".tex") or lower_name.endswith(".zip")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supported formats: .tex template file or .zip template package.",
            )

        templates_root = Path(settings.STORAGE_DIR) / "templates"
        templates_root.mkdir(parents=True, exist_ok=True)
        tpl_dir = templates_root / str(user_id)
        staging_dir = Path(tempfile.mkdtemp(prefix=f".{user_id}-staging-", dir=templates_root))
        backup_dir = None

        try:
            if lower_name.endswith(".zip"):
                try:
                    with zipfile.ZipFile(BytesIO(content), "r") as zip_ref:
                        entries = zip_ref.infolist()
                        if len(entries) > max_archive_files:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="The template archive contains too many files.",
                            )

                        extracted_total = 0
                        for entry in entries:
                            raw_name = entry.filename
                            if not raw_name or "\\" in raw_name:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="The template archive contains an invalid path.",
                                )

                            entry_path = PurePosixPath(raw_name)
                            if entry_path.is_absolute() or any(part == ".." for part in entry_path.parts):
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="The template archive contains an unsafe path traversal.",
                                )

                            mode = entry.external_attr >> 16
                            if stat.S_ISLNK(mode):
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Symbolic links are not allowed in template packages.",
                                )

                            target_path = staging_dir.joinpath(*entry_path.parts)
                            try:
                                target_path.relative_to(staging_dir)
                            except ValueError as exc:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="The template archive escapes the installation directory.",
                                ) from exc

                            if entry.is_dir():
                                target_path.mkdir(parents=True, exist_ok=True)
                                continue

                            extracted_total += entry.file_size
                            if extracted_total > max_extracted_bytes:
                                raise HTTPException(
                                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                    detail="The uncompressed template archive exceeds the size limit.",
                                )

                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            with zip_ref.open(entry, "r") as source, open(target_path, "wb") as dest:
                                shutil.copyfileobj(source, dest)
                except zipfile.BadZipFile as exc:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The uploaded file is not a valid ZIP archive.",
                    ) from exc
            else:
                (staging_dir / "main.tex").write_bytes(content)

            installed_main_tex = staging_dir / "main.tex"
            if not installed_main_tex.exists():
                tex_candidates = [
                    file
                    for file in staging_dir.rglob("*.tex")
                    if file.is_file() and not file.is_symlink()
                ]
                if not tex_candidates:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The template archive must include at least one .tex file.",
                    )

                preferred_main = next(
                    (file for file in tex_candidates if file.stem.lower() in ["main", "resume", "cv"]),
                    None,
                )
                chosen_main = preferred_main or tex_candidates[0]

                if chosen_main.parent == staging_dir:
                    chosen_main.replace(installed_main_tex)
                else:
                    for item in list(chosen_main.parent.iterdir()):
                        dest = staging_dir / item.name
                        if dest.exists():
                            if dest.is_dir():
                                shutil.rmtree(dest)
                            else:
                                dest.unlink()
                        shutil.move(str(item), str(dest))
                    chosen_candidate = staging_dir / chosen_main.name
                    if chosen_candidate.exists():
                        chosen_candidate.replace(installed_main_tex)

            if not installed_main_tex.exists() or installed_main_tex.stat().st_size == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The template must contain a non-empty main .tex file.",
                )

            meta = {
                "filename": Path(filename).name,
                "size_bytes": len(content),
                "updated_at": installed_main_tex.stat().st_mtime,
            }
            (staging_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

            if tpl_dir.exists():
                backup_dir = Path(tempfile.mkdtemp(prefix=f".{user_id}-backup-", dir=templates_root))
                backup_dir.rmdir()
                os.replace(tpl_dir, backup_dir)
            try:
                os.replace(staging_dir, tpl_dir)
            except Exception:
                if backup_dir is not None and backup_dir.exists() and not tpl_dir.exists():
                    os.replace(backup_dir, tpl_dir)
                raise
            if backup_dir is not None and backup_dir.exists():
                shutil.rmtree(backup_dir, ignore_errors=True)

        finally:
            if staging_dir.exists():
                shutil.rmtree(staging_dir, ignore_errors=True)

        return {
            "status": "success",
            "message": f"Custom template '{Path(filename).name}' installed and activated.",
            "filename": Path(filename).name,
            "has_custom_template": True,
        }

    def get_user_template_info(self, user_id: int) -> Dict[str, Any]:
        """Returns metadata about the user's active custom template, or default status."""
        tpl_path = self.get_custom_template_path(user_id)
        if not tpl_path:
            return {
                "has_custom_template": False,
                "template_name": "Data Science / Tech (Default)",
                "filename": None,
                "size": None,
            }

        meta_file = Path(settings.STORAGE_DIR) / "templates" / str(user_id) / "meta.json"
        filename = "custom_template.tex"
        size_str = f"{round(tpl_path.stat().st_size / 1024)} KB"
        if meta_file.exists():
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                filename = data.get("filename", filename)
                size_str = f"{round(data.get('size_bytes', tpl_path.stat().st_size) / 1024)} KB"
            except Exception:
                pass

        return {
            "has_custom_template": True,
            "template_name": filename,
            "filename": filename,
            "size": size_str,
        }

    def delete_user_template(self, user_id: int) -> bool:
        """Removes the custom template for target user, reverting to system default."""
        tpl_dir = Path(settings.STORAGE_DIR) / "templates" / str(user_id)
        if tpl_dir.exists():
            shutil.rmtree(tpl_dir, ignore_errors=True)
            return True
        return False

    def invalidate_user_artifacts(self, db: Session, user_id: int) -> None:
        """Invalidate generated artifacts and validation reports after a template change."""
        artifacts = db.query(ResumeArtifact).filter(ResumeArtifact.user_id == user_id).all()
        artifact_paths = [Path(artifact.file_path) for artifact in artifacts if artifact.file_path]

        for artifact in artifacts:
            db.delete(artifact)

        validations = db.query(ResumeValidation).filter(ResumeValidation.user_id == user_id).all()
        for validation in validations:
            db.delete(validation)

        db.commit()

        for artifact_path in set(artifact_paths):
            referenced = db.query(ResumeArtifact.id).filter(
                ResumeArtifact.file_path == str(artifact_path)
            ).first()
            if not referenced:
                try:
                    artifact_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def _build_summary_code(self, summary: str) -> str:
        """Formats professional summary for the SWE template."""
        s = latex_escape(summary or "").strip()
        if not s:
            return ""
        return f"\\section*{{SUMMARY}}\n{s}\n"

    def _build_education_code(self, educations: list) -> str:
        """Formats education entries into 3 distinct lines:
        Line 1: Degree name on left, dates right-aligned
        Line 2: College / Institution name
        Line 3: CGPA / academic details
        """
        if not educations:
            return ""
        blocks = []
        for edu in educations:
            deg = latex_escape((edu.get("degree") or "").strip())
            inst = latex_escape((edu.get("institution") or edu.get("college") or edu.get("school") or edu.get("university") or "").strip())
            yr = latex_escape((edu.get("year") or edu.get("dates") or edu.get("date") or "").strip())
            raw_gpa = (edu.get("gpa") or edu.get("grade") or edu.get("cgpa") or "").strip()
            gpa = latex_escape(raw_gpa)

            deg_line = f"\\textbf{{{deg}}}"
            if yr:
                deg_line += f"\n\\hfill {yr}"

            lines = [deg_line]
            if inst:
                lines.append(inst)
            if gpa:
                if not any(gpa.lower().startswith(p) for p in ["cgpa", "gpa"]):
                    gpa = f"CGPA: {gpa}"
                lines.append(gpa)

            blocks.append("\n\n".join(lines))

        body = "\n\n".join(b for b in blocks if b)
        return f"\\section*{{EDUCATION}}\n\n{body}\n" if body else ""

    def _build_skills_code(self, skills_dict: Any) -> str:
        """Formats candidate skill categories into the SWE template's format."""
        if not skills_dict or not isinstance(skills_dict, dict):
            return ""
        lines = []
        for cat, items in skills_dict.items():
            if items:
                cat_esc = latex_escape(cat)
                items_esc = ", ".join(latex_escape(i) for i in items if i)
                lines.append(f"\\textbf{{{cat_esc}:}} {items_esc}")
        if not lines:
            return ""
        body = "\n\n".join(lines)
        return f"\\section*{{SKILLS}}\n\n{body}\n"

    def _build_experience_code(self, experiences: list) -> str:
        """Formats work experience entries into SWE template format."""
        if not experiences:
            return ""
        blocks = []
        for exp in experiences:
            title = latex_escape(exp.get("title", ""))
            company = latex_escape(exp.get("company", ""))
            loc = latex_escape(exp.get("location", ""))
            start_date = latex_escape((exp.get("start_date") or "").strip())
            end_date = latex_escape((exp.get("end_date") or "").strip())
            is_current = exp.get("is_current", False)

            if is_current and not end_date:
                end_date = "Present"

            if start_date and end_date:
                dates = f"{start_date}--{end_date}"
            elif start_date:
                dates = start_date
            elif end_date:
                dates = end_date
            else:
                raw_dates = (exp.get("date") or exp.get("dates") or "").strip()
                dates = latex_escape(raw_dates)

            title_line = f"\\textbf{{{title}}}"
            if dates:
                title_line += f" \\hfill {dates}"

            comp_line = f"{company} ({loc})" if (company and loc) else (company or loc)

            bullets = []
            for b in exp.get("bullets", []):
                if b and str(b).strip():
                    cleaned = re.sub(r"^[•\*\-\s]+", "", str(b)).strip()
                    if cleaned:
                        bullets.append(f"\\item {latex_escape(cleaned)}")

            bullets_block = (
                "\\begin{itemize}\n" + "\n".join(bullets) + "\n\\end{itemize}"
                if bullets
                else ""
            )

            parts = [title_line]
            if comp_line:
                parts.append(f"\n{comp_line}")
            if bullets_block:
                parts.append(f"\n{bullets_block}")

            blocks.append("\n".join(parts))

        body = "\n\n".join(b for b in blocks if b)
        return f"\\section*{{EXPERIENCE}}\n\n{body}\n" if body else ""

    def _build_projects_code(self, projects: list) -> str:
        """Formats project entries into SWE template format with proper links."""
        if not projects:
            return ""
        blocks = []
        for proj in projects:
            p_name = latex_escape(proj.get("name", "") or proj.get("title", ""))
            # Links: support both repository and live website URLs
            link_parts = []
            gh_link = (proj.get("github_url") or "").strip()
            live_link = (proj.get("live_url") or "").strip()
            general_link = (proj.get("link") or proj.get("url") or "").strip()

            if gh_link:
                link_parts.append(f"\\href{{{latex_escape(gh_link)}}}{{\\textbf{{ [GitHub]}}}}")
            if live_link:
                link_parts.append(f"\\href{{{latex_escape(live_link)}}}{{\\textbf{{ [Live]}}}}")
            if general_link and not gh_link and not live_link:
                label = "GitHub" if "github.com" in general_link.lower() else "Live"
                link_parts.append(f"\\href{{{latex_escape(general_link)}}}{{\\textbf{{ [{label}]}}}}")

            links_str = " ".join(link_parts)
            if links_str:
                links_str = f" {links_str}"

            # Dates: support start_date, end_date, is_current, and right-alignment
            start_date = latex_escape((proj.get("start_date") or "").strip())
            end_date = latex_escape((proj.get("end_date") or "").strip())
            is_current = proj.get("is_current", False)

            if is_current and not end_date:
                end_date = "Present"

            if start_date and end_date:
                dates_val = f"{start_date}--{end_date}"
            elif start_date:
                dates_val = start_date
            elif end_date:
                dates_val = end_date
            else:
                raw_date = (proj.get("date") or proj.get("year") or proj.get("dates") or "").strip()
                dates_val = latex_escape(raw_date)

            dates_str = f" \\hfill {dates_val}" if dates_val else ""

            header_line = f"\\textbf{{{p_name}}}{links_str}{dates_str}"

            techs = proj.get("technologies", [])
            if isinstance(techs, str):
                techs = [t.strip() for t in techs.split(",") if t.strip()]
            tech_str = ", ".join(latex_escape(t) for t in techs if t) if techs else ""
            tech_line = f"\n\\textit{{{tech_str}}}" if tech_str else ""

            bullets = []
            for b in proj.get("bullets", []):
                if b and str(b).strip():
                    cleaned = re.sub(r"^[•\*\-\s]+", "", str(b)).strip()
                    if cleaned:
                        bullets.append(f"\\item {latex_escape(cleaned)}")

            bullets_block = (
                "\\begin{itemize}\n" + "\n".join(bullets) + "\n\\end{itemize}"
                if bullets
                else ""
            )

            parts = [header_line]
            if tech_line:
                parts.append(tech_line)
            if bullets_block:
                parts.append(f"\n{bullets_block}")

            blocks.append("\n".join(parts))

        body = "\n\n".join(b for b in blocks if b)
        return f"\\section*{{PROJECTS}}\n\n{body}\n" if body else ""

    def _build_certifications_code(self, certifications: list) -> str:
        r"""Formats certifications & achievements into SWE template format with clickable certificate links:
        Format: Certificate Name --- Provider --- \href{<url>}{\underline{Certificate}}
        """
        if not certifications:
            return ""
        bullets = []
        for cert in certifications:
            if isinstance(cert, str):
                cleaned = re.sub(r"^[•\*\-\s]+", "", cert).strip()
                if cleaned:
                    bullets.append(f"\\item {latex_escape(cleaned)}")
            elif isinstance(cert, dict):
                c_name = latex_escape((cert.get("name") or cert.get("title") or "").strip())
                c_issuer = latex_escape((cert.get("issuer") or cert.get("organization") or "").strip())
                cert_url = (
                    cert.get("certificate_url")
                    or cert.get("credential_url")
                    or cert.get("link")
                    or cert.get("url")
                    or ""
                ).strip()

                if c_name:
                    parts = [c_name]
                    if c_issuer:
                        parts.append(c_issuer)
                    if cert_url:
                        parts.append(f"\\href{{{latex_escape(cert_url)}}}{{\\underline{{Certificate}}}}")
                    item_text = " --- ".join(parts)
                    bullets.append(f"\\item {item_text}")

        if not bullets:
            return ""
        return f"\\section*{{CERTIFICATIONS \\& ACHIEVEMENTS}}\n\n\\begin{{itemize}}\n" + "\n".join(bullets) + "\n\\end{itemize}\n"

    def _build_skills_tabular(self, skills_dict: Any) -> str:
        """Formats candidate skill categories into tabular format for custom templates."""
        if not skills_dict or not isinstance(skills_dict, dict):
            return ""
        rows = []
        for cat, items in skills_dict.items():
            if items:
                cat_esc = latex_escape(cat)
                items_esc = ", ".join(latex_escape(i) for i in items)
                rows.append(rf"\skills{{{cat_esc}}} & & {items_esc} \\")
        if not rows:
            return ""
        rows[-1] = re.sub(r"\s*\\\\$", "", rows[-1])
        table_body = "\n".join(rows)
        return f"\\begin{{tabular}}{{p{{11em}} p{{1em}} p{{43em}}}}\n{table_body}\n\\end{{tabular}}"

    def _build_experiences_code(self, experiences: list, projects: list) -> str:
        """Legacy helper combining work experience and technical projects for backwards compatibility."""
        exp_code = self._build_experience_code(experiences)
        proj_code = self._build_projects_code(projects)
        return f"{exp_code}\n\n{proj_code}".strip()

    def _build_activities_code(self, certifications: list) -> str:
        """Legacy helper for activities/certifications for backwards compatibility."""
        return self._build_certifications_code(certifications)

    def render_latex_with_sections(
        self,
        candidate_name: str,
        candidate_email: str,
        phone: str,
        location: str,
        content: Dict[str, Any],
        target_role: str,
        user_id: Optional[int] = None,
        linkedin: Optional[str] = None,
        github: Optional[str] = None,
        portfolio_url: Optional[str] = None,
    ) -> Tuple[str, Dict[str, str]]:
        """Constructs the tailored resume LaTeX document and section files using the default template."""
        # 1. Custom template support (if user uploaded a custom template)
        custom_tpl_path = self.get_custom_template_path(user_id)
        if custom_tpl_path and custom_tpl_path.exists():
            try:
                tpl_text = custom_tpl_path.read_text(encoding="utf-8")
                injected = self._inject_into_custom_template(
                    tpl_text,
                    name_esc=latex_escape(candidate_name or "Candidate"),
                    role_esc=latex_escape(target_role or "Software Engineer"),
                    contact_line=" $\\cdot$ ".join(p for p in [latex_escape(candidate_email or ""), latex_escape(phone or ""), latex_escape(location or "")] if p),
                    email_esc=latex_escape(candidate_email or ""),
                    phone_esc=latex_escape(phone or ""),
                    loc_esc=latex_escape(location or ""),
                    summary=latex_escape(content.get("summary", "")),
                    skills_block=self._build_skills_tabular(content.get("skills", {})),
                    experiences_section=self._build_experiences_code(content.get("experience", []), content.get("projects", [])),
                    projects_section="",
                    education_section=self._build_education_code(content.get("education", [])),
                    certifications_section=self._build_activities_code(content.get("certifications", [])),
                    linkedin_esc=latex_escape(linkedin or ""),
                    github_esc=latex_escape(github or ""),
                )
                return injected, {}
            except Exception as exc:
                logger.warning(
                    "User %s custom template content injection failed (%s). Falling back to system default template.",
                    user_id,
                    exc,
                )

        # 2. Render using the single, fixed default template (Timmy Chan data science / tech template)
        name_esc = latex_escape(candidate_name or "Candidate")
        phone_esc = latex_escape(phone or "")
        city_esc = latex_escape(location or "")
        email_esc = latex_escape(candidate_email or "")
        role_esc = latex_escape(target_role or "Software Engineer")

        clean_github = (github or "").strip()
        clean_github = re.sub(r"^(?:https?://)?(?:www\.)?github\.com/", "", clean_github, flags=re.IGNORECASE).strip("/")
        github_def = latex_escape(clean_github)

        raw_linkedin = (linkedin or "").strip()
        if raw_linkedin:
            if raw_linkedin.startswith("http://") or raw_linkedin.startswith("https://"):
                full_linkedin_url = raw_linkedin
            elif "linkedin.com" in raw_linkedin.lower():
                full_linkedin_url = f"https://{raw_linkedin.lstrip('/')}"
            else:
                full_linkedin_url = f"https://www.linkedin.com/in/{raw_linkedin.strip('/')}"

            in_match = re.search(r"linkedin\.com/in/([a-zA-Z0-9_\-\.]+)/?", raw_linkedin, flags=re.IGNORECASE)
            if in_match:
                linkedin_handle = in_match.group(1)
            else:
                clean = re.sub(r"^(?:https?://)?(?:[a-zA-Z0-9_\-]+\.)?linkedin\.com/?", "", raw_linkedin, flags=re.IGNORECASE).strip("/")
                linkedin_handle = clean if clean else "profile"
        else:
            full_linkedin_url = ""
            linkedin_handle = ""

        linkedin_def = latex_escape(linkedin_handle)
        linkedin_url_def = latex_escape(full_linkedin_url)

        port_url = portfolio_url or ""
        portfoliourl_def = latex_escape(port_url)
        clean_port_name = re.sub(r"^https?://", "", port_url).strip("/")
        portfolioname_def = latex_escape(clean_port_name)

        sections_map: Dict[str, str] = {}

        # 1. SUMMARY
        summary = content.get("summary", "")
        sections_map["summary"] = self._build_summary_code(summary)
        sections_map["objective"] = sections_map["summary"]

        # 2. EDUCATION
        educations = content.get("education", [])
        sections_map["education"] = self._build_education_code(educations)

        # 3. SKILLS
        skills = content.get("skills", {})
        sections_map["skills"] = self._build_skills_code(skills)

        # 4. EXPERIENCE
        experiences = content.get("experience", [])
        sections_map["experience"] = self._build_experience_code(experiences)

        # 5. PROJECTS
        projects = content.get("projects", [])
        sections_map["projects"] = self._build_projects_code(projects)

        # 6. CERTIFICATIONS & ACHIEVEMENTS
        certifications = content.get("certifications", [])
        sections_map["certifications"] = self._build_certifications_code(certifications)
        sections_map["activities"] = sections_map["certifications"]

        resume_tpl_path = DEFAULT_TEMPLATE_DIR / "resume.tex"
        if not resume_tpl_path.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default resume.tex template not found.",
            )

        resume_tex = resume_tpl_path.read_text(encoding="utf-8")

        def_replacements = [
            (r"\\def\\name\{[^}]*\}", f"\\def\\name{{{name_esc}}}"),
            (r"\\def\\phone\{[^}]*\}", f"\\def\\phone{{{phone_esc}}}"),
            (r"\\def\\city\{[^}]*\}", f"\\def\\city{{{city_esc}}}"),
            (r"\\def\\email\{[^}]*\}", f"\\def\\email{{{email_esc}}}"),
            (r"\\def\\LinkedIn\{[^}]*\}", f"\\def\\LinkedIn{{{linkedin_def}}}"),
            (r"\\def\\linkedin\{[^}]*\}", f"\\def\\linkedin{{{linkedin_def}}}"),
            (r"\\def\\linkedinurl\{[^}]*\}", f"\\def\\linkedinurl{{{linkedin_url_def}}}"),
            (r"\\def\\github\{[^}]*\}", f"\\def\\github{{{github_def}}}"),
            (r"\\def\\role\{[^}]*\}", f"\\def\\role{{{role_esc}}}"),
            (r"\\def\\portfoliourl\{[^}]*\}", f"\\def\\portfoliourl{{{portfoliourl_def}}}"),
            (r"\\def\\portfolioname\{[^}]*\}", f"\\def\\portfolioname{{{portfolioname_def}}}"),
        ]
        for pattern, repl in def_replacements:
            resume_tex = re.sub(pattern, lambda m, r=repl: r, resume_tex)

        if not sections_map["summary"].strip():
            resume_tex = resume_tex.replace(r"\input{sections/summary}", "")
            resume_tex = resume_tex.replace(r"\input{sections/objective}", "")
        if not sections_map["education"].strip():
            resume_tex = resume_tex.replace(r"\input{sections/education}", "")
            resume_tex = re.sub(r"\\section\*?\{Education\}\s*\\input\{sections/education\}", "", resume_tex, flags=re.IGNORECASE)
        if not sections_map["skills"].strip():
            resume_tex = resume_tex.replace(r"\input{sections/skills}", "")
            resume_tex = re.sub(r"\\section\*?\{Skills\}\s*\\input\{sections/skills\}", "", resume_tex, flags=re.IGNORECASE)
        if not sections_map["experience"].strip():
            resume_tex = resume_tex.replace(r"\input{sections/experience}", "")
            resume_tex = re.sub(r"\\section\*?\{(?:Technical )?Experience\}\s*\\input\{sections/experience\}", "", resume_tex, flags=re.IGNORECASE)
        if not sections_map["projects"].strip():
            resume_tex = resume_tex.replace(r"\input{sections/projects}", "")
            resume_tex = re.sub(r"\\section\*?\{Projects\}\s*\\input\{sections/projects\}", "", resume_tex, flags=re.IGNORECASE)
        if not sections_map["certifications"].strip():
            resume_tex = resume_tex.replace(r"\input{sections/certifications}", "")
            resume_tex = resume_tex.replace(r"\input{sections/activities}", "")
            resume_tex = re.sub(r"\\section\*?\{(?:Certifications.*?|Activities)\}\s*\\input\{sections/(?:certifications|activities)\}", "", resume_tex, flags=re.IGNORECASE)

        return resume_tex, sections_map

    def render_latex(
        self,
        candidate_name: str,
        candidate_email: str,
        phone: str,
        location: str,
        content: Dict[str, Any],
        target_role: str,
        user_id: Optional[int] = None,
        linkedin: Optional[str] = None,
        github: Optional[str] = None,
        portfolio_url: Optional[str] = None,
    ) -> str:
        """Constructs a clean LaTeX document using the single fixed default template."""
        tex_source, _ = self.render_latex_with_sections(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            phone=phone,
            location=location,
            content=content,
            target_role=target_role,
            user_id=user_id,
            linkedin=linkedin,
            github=github,
            portfolio_url=portfolio_url,
        )
        return tex_source

    def _inject_into_custom_template(
        self,
        template_text: str,
        name_esc: str,
        role_esc: str,
        contact_line: str,
        email_esc: str,
        phone_esc: str,
        loc_esc: str,
        summary: str,
        skills_block: str,
        experiences_section: str,
        projects_section: str,
        education_section: str,
        certifications_section: str = "",
        linkedin_esc: str = "",
        github_esc: str = "",
    ) -> str:
        """Injects tailored candidate content into user-provided LaTeX template."""
        text = template_text

        replacements = {
            "{{NAME}}": name_esc,
            "{{ROLE}}": role_esc,
            "{{TITLE}}": role_esc,
            "{{HEADLINE}}": role_esc,
            "{{CONTACT}}": contact_line,
            "{{EMAIL}}": email_esc,
            "{{PHONE}}": phone_esc,
            "{{LOCATION}}": loc_esc,
            "{{LINKEDIN}}": linkedin_esc,
            "{{GITHUB}}": github_esc,
            "{{SUMMARY}}": summary,
            "{{SKILLS}}": skills_block,
            "{{EXPERIENCE}}": experiences_section,
            "{{WORK_EXPERIENCE}}": experiences_section,
            "{{PROJECTS}}": projects_section,
            "{{EDUCATION}}": education_section,
            "{{CERTIFICATIONS}}": certifications_section,
            "{{CERTIFICATES}}": certifications_section,
            "<<NAME>>": name_esc,
            "<<ROLE>>": role_esc,
            "<<CONTACT>>": contact_line,
            "<<EMAIL>>": email_esc,
            "<<PHONE>>": phone_esc,
            "<<LOCATION>>": loc_esc,
            "<<LINKEDIN>>": linkedin_esc,
            "<<GITHUB>>": github_esc,
            "<<SUMMARY>>": summary,
            "<<SKILLS>>": skills_block,
            "<<EXPERIENCE>>": experiences_section,
            "<<PROJECTS>>": projects_section,
            "<<EDUCATION>>": education_section,
            "<<CERTIFICATIONS>>": certifications_section,
            "<<CERTIFICATES>>": certifications_section,
        }

        replaced_count = 0
        for placeholder, val in replacements.items():
            if placeholder in text:
                text = text.replace(placeholder, val)
                replaced_count += 1

        if replaced_count == 0:
            text = re.sub(r"(\\name\{)[^}]*(\})", lambda m: f"{m.group(1)}{name_esc}{m.group(2)}", text, count=1)
            text = re.sub(r"(\\author\{)[^}]*(\})", lambda m: f"{m.group(1)}{name_esc}{m.group(2)}", text, count=1)
            text = re.sub(r"(\\Huge\s*(?:\\textbf)?\{)[^}]*(\})", lambda m: f"{m.group(1)}{name_esc}{m.group(2)}", text, count=1)

            if "\\address" in text:
                addr_lines = []
                line1 = " \\\\ ".join([p for p in [phone_esc, loc_esc] if p])
                if line1:
                    addr_lines.append(f"\\address{{{line1}}}")
                line2_parts = []
                if email_esc:
                    line2_parts.append(f"\\href{{mailto:{email_esc}}}{{{email_esc}}}")
                if github_esc:
                    line2_parts.append(f"\\href{{{github_esc}}}{{\\underline{{GitHub}}}}")
                if linkedin_esc:
                    line2_parts.append(f"\\href{{{linkedin_esc}}}{{\\underline{{LinkedIn}}}}")
                if line2_parts:
                    addr_lines.append(f"\\address{{{ ' \\,|\\, '.join(line2_parts) }}}")
                elif not addr_lines and contact_line:
                    addr_lines.append(f"\\address{{{contact_line}}}")

                if addr_lines:
                    addr_block = "\n".join(addr_lines) + "\n\n"
                    if re.search(r"\\name\{[^\}]*\}([\s\S]*?)\\begin\{document\}", text):
                        text = re.sub(
                            r"(\\name\{[^\}]*\})([\s\S]*?)(\\begin\{document\})",
                            lambda m, ab=addr_block: f"{m.group(1)}\n{ab}{m.group(3)}",
                            text,
                            count=1,
                        )
                    else:
                        text = re.sub(
                            r"([\s\S]*?)(\\begin\{document\})",
                            lambda m, ab=addr_block: f"{ab}{m.group(2)}",
                            text,
                            count=1,
                        )

            rsec_map = [
                (r"\\begin\{rSection\}\{(?i:Summary|Professional Summary)\}", summary, "SUMMARY"),
                (r"\\begin\{rSection\}\{(?i:Skills|Technical Skills|Competencies)\}", skills_block, "SKILLS"),
                (r"\\begin\{rSection\}\{(?i:Experience|Work Experience|Professional Experience)\}", experiences_section, "EXPERIENCE"),
                (r"\\begin\{rSection\}\{(?i:Projects|Key Projects|Personal Projects)\}", projects_section, "PROJECTS"),
                (r"\\begin\{rSection\}\{(?i:Education|Academic Background)\}", education_section, "EDUCATION"),
                (r"\\begin\{rSection\}\{(?i:Certificates|Certifications)\}", certifications_section, "CERTIFICATIONS"),
            ]
            for pat_prefix, content_str, title in rsec_map:
                full_pat = pat_prefix + r"\s*[\s\S]*?\\end\{rSection\}"
                if re.search(full_pat, text):
                    if content_str.strip():
                        text = re.sub(
                            full_pat,
                            lambda m, c=content_str, t=title: f"\\begin{{rSection}}{{{t}}}\n\n{c}\n\n\\end{{rSection}}",
                            text,
                            count=1,
                        )
                    else:
                        text = re.sub(full_pat, "", text, count=1)

            sample_rsections = [
                r"\\begin\{rSection\}\{(?i:Leadership|Leadership Experience)\}\s*[\s\S]*?\\end\{rSection\}",
                r"\\begin\{rSection\}\{(?i:Achievements|Honors|Awards)\}\s*[\s\S]*?\\end\{rSection\}",
                r"\\begin\{rSection\}\{(?i:Volunteer|Extracurricular|Activities)\}\s*[\s\S]*?\\end\{rSection\}",
                r"\\begin\{rSection\}\{(?i:Publications|Interests)\}\s*[\s\S]*?\\end\{rSection\}",
            ]
            for pat in sample_rsections:
                text = re.sub(pat, "", text)

            sec_map = [
                (r"(\\section\*?\{(?i:Professional Summary|Summary)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)", summary),
                (r"(\\section\*?\{(?i:Skills|Technical Skills|Competencies|Technical Competencies)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)", skills_block),
                (r"(\\section\*?\{(?i:Experience|Work Experience|Professional Experience)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)", experiences_section),
                (r"(\\section\*?\{(?i:Projects|Key Projects|Personal Projects)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)", projects_section),
                (r"(\\section\*?\{(?i:Education|Academic Background)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)", education_section),
                (r"(\\section\*?\{(?i:Certificates|Certifications)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)", certifications_section),
            ]
            for pattern, content_str in sec_map:
                if re.search(pattern, text):
                    text = re.sub(pattern, lambda m, c=content_str: f"{m.group(1)}{c}\n\n", text, count=1)

        safe_href_shim = (
            "\\providecommand{\\href}[2]{\\underline{#2}}\n"
            "\\providecommand{\\url}[1]{\\texttt{#1}}\n"
            "\\providecommand{\\hypersetup}[1]{}\n"
            "\\providecommand{\\skills}[1]{\\textbf{#1}}\n"
            "\\providecommand{\\subtext}[1]{\\textbf{#1}\\par}\n"
            "\\ifdefined\\zitemize\\else\\newenvironment{zitemize}{\\begin{itemize}}{\\end{itemize}}\\fi\n"
        )
        if "\\usepackage{hyperref}" in text:
            text = text.replace("\\usepackage{hyperref}", safe_href_shim)
        elif "\\begin{document}" in text:
            text = text.replace("\\begin{document}", f"{safe_href_shim}\\begin{{document}}")

        return text

    def compile_pdf(
        self,
        tex_content: str,
        output_base_name: str,
        target_dir: Path,
        user_id: Optional[int] = None,
        sections: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Compiles LaTeX source code into PDF via pdflatex within an isolated temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 1. Copy default template dependencies (TLCresume.sty, _header.tex) into compilation workspace
            if DEFAULT_TEMPLATE_DIR.exists():
                for item in DEFAULT_TEMPLATE_DIR.glob("*"):
                    if item.is_file() and item.name not in ["resume.tex", "data_science_tech_resume_template.pdf", "data_science_tech_resume_template_multipage.pdf"]:
                        shutil.copy2(item, tmp_path / item.name)

            # 2. Set up sections directory
            sec_dir = tmp_path / "sections"
            sec_dir.mkdir(parents=True, exist_ok=True)
            if sections:
                for sec_name, sec_str in sections.items():
                    (sec_dir / f"{sec_name}.tex").write_text(sec_str, encoding="utf-8")
            elif (DEFAULT_TEMPLATE_DIR / "sections").exists():
                for sec_file in (DEFAULT_TEMPLATE_DIR / "sections").glob("*.tex"):
                    shutil.copy2(sec_file, sec_dir / sec_file.name)

            # 3. User custom template dependencies (.cls, .sty, images) if custom template is present
            if user_id:
                tpl_dir = self.get_user_template_dir(user_id)
                if tpl_dir.exists():
                    for item in tpl_dir.rglob("*"):
                        if not item.is_file() or item.is_symlink() or item.name in ["main.tex", "meta.json"]:
                            continue
                        relative_path = item.relative_to(tpl_dir)
                        dest_file = tmp_path / relative_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_file)
                        if item.suffix == ".cls":
                            try:
                                cls_text = dest_file.read_text(encoding="utf-8")
                                cls_text = cls_text.replace(
                                    r"\usepackage[parfill]{parskip}",
                                    r"\setlength{\parindent}{0pt}\setlength{\parskip}{0.5\baselineskip}",
                                )
                                cls_text = cls_text.replace(
                                    r"\usepackage{hyperref}",
                                    r"\providecommand{\href}[2]{#2}\providecommand{\url}[1]{\texttt{#1}}\providecommand{\hypersetup}[1]{}",
                                )
                                cls_text = re.sub(r'\\hypersetup\{[^}]*\}', '', cls_text)
                                dest_file.write_text(cls_text, encoding="utf-8")
                            except Exception:
                                pass

            cleaned_tex = tex_content
            tex_file = tmp_path / f"{output_base_name}.tex"
            tex_file.write_text(cleaned_tex, encoding="utf-8")

            cmd = [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-disable-installer",
                "-no-shell-escape",
                f"{output_base_name}.tex",
            ]

            compile_env = os.environ.copy()
            compile_env["openin_any"] = "p"
            compile_env["openout_any"] = "p"
            compile_env["TEXMFOUTPUT"] = str(tmp_path)

            process = subprocess.run(
                cmd,
                cwd=tmp_path,
                env=compile_env,
                capture_output=True,
                text=True,
                timeout=20,
            )

            compiled_pdf = tmp_path / f"{output_base_name}.pdf"
            if (
                process.returncode != 0
                or not compiled_pdf.is_file()
                or compiled_pdf.stat().st_size == 0
            ):
                error_log = "\n".join(
                    part for part in (process.stdout, process.stderr) if part
                )
                error_lines = [
                    line
                    for line in error_log.splitlines()
                    if line.startswith("!") or "error" in line.lower()
                ][:10]
                summary_err = (
                    "\n".join(error_lines)
                    if error_lines
                    else "LaTeX compilation failed."
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Compilation error: {summary_err}",
                )

            target_dir.mkdir(parents=True, exist_ok=True)
            dest_pdf = target_dir / f"{output_base_name}.pdf"
            dest_tex = target_dir / f"{output_base_name}.tex"

            shutil.copyfile(compiled_pdf, dest_pdf)
            shutil.copyfile(tex_file, dest_tex)

            target_sec_dir = target_dir / "sections"
            target_sec_dir.mkdir(parents=True, exist_ok=True)
            for s_file in sec_dir.glob("*.tex"):
                shutil.copyfile(s_file, target_sec_dir / s_file.name)
            if (tmp_path / "TLCresume.sty").exists():
                shutil.copyfile(tmp_path / "TLCresume.sty", target_dir / "TLCresume.sty")
            if (tmp_path / "_header.tex").exists():
                shutil.copyfile(tmp_path / "_header.tex", target_dir / "_header.tex")

            return {
                "pdf_path": str(dest_pdf),
                "tex_path": str(dest_tex),
                "pdf_size": dest_pdf.stat().st_size,
                "log": process.stdout,
            }

    def generate_resume_artifacts(self, db: Session, user: User, resume_id: int) -> Dict[str, Any]:
        """Orchestrates tailored resume content injection, LaTeX compilation, and artifact persistence."""
        resume = db.query(TailoredResume).filter(
            TailoredResume.id == resume_id,
            TailoredResume.user_id == user.id,
        ).first()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tailored resume not found or access unauthorized",
            )

        from app.services.resolution_service import resolution_service

        effective_content, provenance = resolution_service.resolve_effective_content(
            db=db, user=user, resume=resume
        )

        contact = effective_content.get("contact_info", {})
        phone = contact.get("phone") or ""
        location = contact.get("location") or ""
        linkedin = contact.get("linkedin") or contact.get("linkedin_url") or ""
        github = contact.get("github") or contact.get("github_url") or ""
        portfolio = contact.get("portfolio") or contact.get("portfolio_url") or ""

        tex_source, sections_map = self.render_latex_with_sections(
            candidate_name=user.full_name or "Candidate",
            candidate_email=user.email,
            phone=phone,
            location=location,
            linkedin=linkedin,
            github=github,
            portfolio_url=portfolio,
            content=effective_content,
            target_role=resume.target_role or "Software Engineer",
            user_id=user.id,
        )

        user_storage = self.get_user_artifact_dir(user.id)
        base_name = f"resume_v{resume.version_number}_job{resume.job_id}"

        try:
            compile_result = self.compile_pdf(tex_source, base_name, user_storage, user_id=user.id, sections=sections_map)
        except HTTPException as exc:
            if user.id and self.get_custom_template_path(user.id):
                logger.warning(
                    "User %s custom template compilation failed (%s). Falling back to system default template.",
                    user.id,
                    exc.detail,
                )
                tex_source, sections_map = self.render_latex_with_sections(
                    candidate_name=user.full_name or "Candidate",
                    candidate_email=user.email,
                    phone=phone,
                    location=location,
                    linkedin=linkedin,
                    github=github,
                    portfolio_url=portfolio,
                    content=effective_content,
                    target_role=resume.target_role or "Software Engineer",
                    user_id=None,
                )
                compile_result = self.compile_pdf(tex_source, base_name, user_storage, user_id=None, sections=sections_map)
            else:
                raise exc

        pdf_artifact = db.query(ResumeArtifact).filter(
            ResumeArtifact.tailored_resume_id == resume.id,
            ResumeArtifact.user_id == user.id,
            ResumeArtifact.artifact_type == "pdf",
        ).first()
        if not pdf_artifact:
            pdf_artifact = ResumeArtifact(
                tailored_resume_id=resume.id,
                user_id=user.id,
                artifact_type="pdf",
                file_path=compile_result["pdf_path"],
                file_size=compile_result["pdf_size"],
                compilation_log=compile_result["log"][-2000:],
            )
            db.add(pdf_artifact)
        else:
            pdf_artifact.file_path = compile_result["pdf_path"]
            pdf_artifact.file_size = compile_result["pdf_size"]
            pdf_artifact.compilation_log = compile_result["log"][-2000:]

        tex_artifact = db.query(ResumeArtifact).filter(
            ResumeArtifact.tailored_resume_id == resume.id,
            ResumeArtifact.user_id == user.id,
            ResumeArtifact.artifact_type == "tex",
        ).first()
        if not tex_artifact:
            tex_artifact = ResumeArtifact(
                tailored_resume_id=resume.id,
                user_id=user.id,
                artifact_type="tex",
                file_path=compile_result["tex_path"],
                file_size=len(tex_source.encode("utf-8")),
                compilation_log=None,
            )
            db.add(tex_artifact)
        else:
            tex_artifact.file_path = compile_result["tex_path"]
            tex_artifact.file_size = len(tex_source.encode("utf-8"))

        db.commit()
        db.refresh(pdf_artifact)
        db.refresh(tex_artifact)

        return {
            "status": "success",
            "message": "Resume PDF generated successfully via LaTeX.",
            "pdf_artifact": pdf_artifact,
            "tex_artifact": tex_artifact,
            "provenance": provenance,
        }


latex_service = LatexService()
