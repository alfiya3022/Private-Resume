import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.user import User
from app.models.tailored_resume import TailoredResume
from app.models.profile import CandidateProfile
from app.models.artifact import ResumeArtifact


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

    def render_latex(self, candidate_name: str, candidate_email: str, phone: str, location: str, content: Dict[str, Any], target_role: str) -> str:
        """Constructs an ATS-compliant, single/two-page clean LaTeX document."""
        role_esc = latex_escape(target_role or "Software Engineer")
        name_esc = latex_escape(candidate_name or "Candidate")
        email_esc = latex_escape(candidate_email or "")
        phone_esc = latex_escape(phone or "")
        loc_esc = latex_escape(location or "")

        contact_parts = [p for p in [email_esc, phone_esc, loc_esc] if p]
        contact_line = " $\\cdot$ ".join(contact_parts)

        # Summary
        summary = latex_escape(content.get("summary", ""))

        # Skills
        skills_dict = content.get("skills", {})
        skills_lines = []
        if isinstance(skills_dict, dict):
            for cat, items in skills_dict.items():
                if items:
                    cat_esc = latex_escape(cat)
                    items_esc = ", ".join(latex_escape(i) for i in items)
                    skills_lines.append(f"\\textbf{{{cat_esc}:}} {items_esc} \\\\")
        skills_block = "\n".join(skills_lines)

        # Experience
        exp_blocks = []
        for exp in content.get("experience", []):
            title = latex_escape(exp.get("title", ""))
            company = latex_escape(exp.get("company", ""))
            exp_loc = latex_escape(exp.get("location", ""))
            start_date = latex_escape(exp.get("start_date", ""))
            end_date = latex_escape(exp.get("end_date", "Present"))
            
            bullets = [f"  \\item {latex_escape(b)}" for b in exp.get("bullets", []) if b]
            bullets_block = "\n".join(bullets) if bullets else "  \\item Key contributions and engineering deliverables."

            loc_str = f" -- {exp_loc}" if exp_loc else ""
            dates = f"{start_date} -- {end_date}" if start_date else end_date

            exp_block = f"""\\textbf{{{title}}} $\\cdot$ \\textit{{{company}}}{loc_str} \\hfill {{{dates}}}
\\begin{{itemize}}
{bullets_block}
\\end{{itemize}}
\\vspace{{3pt}}"""
            exp_blocks.append(exp_block)
        experiences_section = "\n\n".join(exp_blocks)

        # Projects
        proj_blocks = []
        for p in content.get("projects", []):
            p_name = latex_escape(p.get("name", ""))
            techs = p.get("technologies", [])
            tech_str = f" ({latex_escape(', '.join(techs))})" if techs else ""
            p_bullets = [f"  \\item {latex_escape(b)}" for b in p.get("bullets", []) if b]
            bullets_block = "\n".join(p_bullets) if p_bullets else "  \\item Implemented and deployed project solution."

            proj_block = f"""\\textbf{{{p_name}}}{tech_str}
\\begin{{itemize}}
{bullets_block}
\\end{{itemize}}
\\vspace{{3pt}}"""
            proj_blocks.append(proj_block)
        projects_section = "\n\n".join(proj_blocks)

        # Education
        edu_blocks = []
        for edu in content.get("education", []):
            deg = latex_escape(edu.get("degree", ""))
            inst = latex_escape(edu.get("institution", ""))
            yr = latex_escape(edu.get("year", ""))
            gpa = latex_escape(edu.get("gpa", ""))
            gpa_str = f" $\\cdot$ {gpa}" if gpa else ""
            yr_str = f" \\hfill {{{yr}}}" if yr else ""

            edu_blocks.append(f"\\textbf{{{deg}}} $\\cdot$ \\textit{{{inst}}}{gpa_str}{yr_str} \\\\")
        education_section = "\n".join(edu_blocks)

        # Assemble document using core LaTeX primitives (zero external dependencies required)
        tex = f"""\\documentclass[10pt]{{article}}
\\setlength{{\\topmargin}}{{-0.5in}}
\\setlength{{\\textheight}}{{9.5in}}
\\setlength{{\\oddsidemargin}}{{-0.25in}}
\\setlength{{\\evensidemargin}}{{-0.25in}}
\\setlength{{\\textwidth}}{{7.0in}}
\\setlength{{\\parindent}}{{0pt}}
\\pagestyle{{empty}}

\\begin{{document}}

% HEADER
\\begin{{center}}
  {{\\Huge \\textbf{{{name_esc}}}}} \\\\[4pt]
  {{\\large \\textbf{{{role_esc}}}}} \\\\[4pt]
  {{{contact_line}}}
\\end{{center}}

\\vspace{{6pt}}
\\hrule
\\vspace{{8pt}}

% PROFESSIONAL SUMMARY
\\textbf{{\\large PROFESSIONAL SUMMARY}} \\\\[3pt]
{{{summary}}}

\\vspace{{10pt}}

% TECHNICAL SKILLS
\\textbf{{\\large TECHNICAL COMPETENCIES}} \\\\[4pt]
{skills_block}

\\vspace{{10pt}}

% EXPERIENCE
\\textbf{{\\large PROFESSIONAL EXPERIENCE}} \\\\[4pt]
{experiences_section}

\\vspace{{6pt}}

% PROJECTS
\\textbf{{\\large KEY PROJECTS}} \\\\[4pt]
{projects_section}

\\vspace{{6pt}}

% EDUCATION
\\textbf{{\\large EDUCATION}} \\\\[4pt]
{education_section}

\\end{{document}}
"""
        return tex

    def compile_pdf(self, tex_content: str, output_base_name: str, target_dir: Path) -> Dict[str, Any]:
        """Compiles LaTeX source code into PDF via pdflatex within an isolated temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            tex_file = tmp_path / f"{output_base_name}.tex"
            tex_file.write_text(tex_content, encoding="utf-8")

            # Run pdflatex safely: -no-shell-escape forbids external command execution
            cmd = [
                "pdflatex",
                "-interaction=nonstopmode",
                "-no-shell-escape",
                f"{output_base_name}.tex",
            ]

            process = subprocess.run(
                cmd,
                cwd=tmp_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            compiled_pdf = tmp_path / f"{output_base_name}.pdf"
            if not compiled_pdf.exists():
                error_log = process.stdout or process.stderr
                # Extract error lines for user feedback
                error_lines = [l for l in error_log.splitlines() if l.startswith("!") or "error" in l.lower()][:10]
                summary_err = "\n".join(error_lines) if error_lines else "LaTeX compilation failed."
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Compilation error: {summary_err}",
                )

            # Persist files into target user directory
            dest_pdf = target_dir / f"{output_base_name}.pdf"
            dest_tex = target_dir / f"{output_base_name}.tex"

            shutil.copyfile(compiled_pdf, dest_pdf)
            shutil.copyfile(tex_file, dest_tex)

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

        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        phone = profile.phone if profile else ""
        location = profile.location if profile else ""

        # Render LaTeX
        tex_source = self.render_latex(
            candidate_name=user.full_name or "Candidate",
            candidate_email=user.email,
            phone=phone,
            location=location,
            content=resume.content or {},
            target_role=resume.target_role or "Software Engineer",
        )

        user_storage = self.get_user_artifact_dir(user.id)
        base_name = f"resume_v{resume.version_number}_job{resume.job_id}"

        # Compile PDF
        compile_result = self.compile_pdf(tex_source, base_name, user_storage)

        # Save/update PDF artifact
        pdf_artifact = db.query(ResumeArtifact).filter(
            ResumeArtifact.tailored_resume_id == resume.id,
            ResumeArtifact.artifact_type == "pdf",
        ).first()
        if not pdf_artifact:
            pdf_artifact = ResumeArtifact(
                tailored_resume_id=resume.id,
                user_id=user.id,
                artifact_type="pdf",
                file_path=compile_result["pdf_path"],
                file_size=compile_result["pdf_size"],
                compilation_log=compile_result["log"][-2000:],  # Store summary log
            )
            db.add(pdf_artifact)
        else:
            pdf_artifact.file_path = compile_result["pdf_path"]
            pdf_artifact.file_size = compile_result["pdf_size"]
            pdf_artifact.compilation_log = compile_result["log"][-2000:]

        # Save/update TeX artifact
        tex_artifact = db.query(ResumeArtifact).filter(
            ResumeArtifact.tailored_resume_id == resume.id,
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
        }


latex_service = LatexService()
