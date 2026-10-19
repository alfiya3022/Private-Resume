import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
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
        """Saves or extracts user-provided LaTeX template (.tex or .zip)."""
        tpl_dir = self.get_user_template_dir(user_id)
        # Clear previous custom template files
        for item in tpl_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        lower_name = filename.lower()
        if lower_name.endswith(".zip"):
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
                tmp_zip.write(content)
                tmp_zip_path = Path(tmp_zip.name)
            try:
                with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tpl_dir)
                # Find the primary .tex file
                tex_files = list(tpl_dir.glob("*.tex"))
                if not tex_files:
                    tex_files = list(tpl_dir.rglob("*.tex"))
                if not tex_files:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The uploaded .zip package must contain at least one .tex template file.",
                    )
                # Ensure main.tex exists
                main_tex = tpl_dir / "main.tex"
                if not main_tex.exists():
                    shutil.copy2(tex_files[0], main_tex)
            finally:
                if tmp_zip_path.exists():
                    tmp_zip_path.unlink()
        elif lower_name.endswith(".tex"):
            (tpl_dir / "main.tex").write_bytes(content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supported formats: .tex template file or .zip template package.",
            )

        # Store metadata
        meta = {
            "filename": filename,
            "size_bytes": len(content),
            "updated_at": Path(tpl_dir / "main.tex").stat().st_mtime,
        }
        (tpl_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

        return {
            "status": "success",
            "message": f"Custom template '{filename}' installed and activated.",
            "filename": filename,
            "has_custom_template": True,
        }

    def get_user_template_info(self, user_id: int) -> Dict[str, Any]:
        """Returns metadata about the user's active custom template, or default status."""
        tpl_path = self.get_custom_template_path(user_id)
        if not tpl_path:
            return {
                "has_custom_template": False,
                "template_name": "Modern Editorial (System Default)",
                "filename": None,
                "size": None,
            }

        meta_file = Path(settings.STORAGE_DIR) / "templates" / str(user_id) / "meta.json"
        filename = "custom_template.tex"
        size_str = f"{Math_round(tpl_path.stat().st_size / 1024) if hasattr(tpl_path, 'size') else round(tpl_path.stat().st_size / 1024)} KB"
        date_str = ""
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

    def render_latex(
        self,
        candidate_name: str,
        candidate_email: str,
        phone: str,
        location: str,
        content: Dict[str, Any],
        target_role: str,
        user_id: Optional[int] = None,
    ) -> str:
        """Constructs a clean LaTeX document using either user-provided template or default ATS template."""
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

        # Check for user-provided custom LaTeX template
        custom_tpl_path = self.get_custom_template_path(user_id)
        if custom_tpl_path and custom_tpl_path.exists():
            try:
                tpl_text = custom_tpl_path.read_text(encoding="utf-8")
                return self._inject_into_custom_template(
                    tpl_text,
                    name_esc=name_esc,
                    role_esc=role_esc,
                    contact_line=contact_line,
                    email_esc=email_esc,
                    phone_esc=phone_esc,
                    loc_esc=loc_esc,
                    summary=summary,
                    skills_block=skills_block,
                    experiences_section=experiences_section,
                    projects_section=projects_section,
                    education_section=education_section,
                )
            except Exception:
                # If custom template parse fails, gracefully fall back to default
                pass

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
    ) -> str:
        """Injects tailored candidate content into user-provided LaTeX template."""
        text = template_text

        # 1. Direct placeholder replacements
        replacements = {
            "{{NAME}}": name_esc,
            "{{ROLE}}": role_esc,
            "{{TITLE}}": role_esc,
            "{{HEADLINE}}": role_esc,
            "{{CONTACT}}": contact_line,
            "{{EMAIL}}": email_esc,
            "{{PHONE}}": phone_esc,
            "{{LOCATION}}": loc_esc,
            "{{SUMMARY}}": summary,
            "{{SKILLS}}": skills_block,
            "{{EXPERIENCE}}": experiences_section,
            "{{WORK_EXPERIENCE}}": experiences_section,
            "{{PROJECTS}}": projects_section,
            "{{EDUCATION}}": education_section,
            "<<NAME>>": name_esc,
            "<<ROLE>>": role_esc,
            "<<CONTACT>>": contact_line,
            "<<EMAIL>>": email_esc,
            "<<PHONE>>": phone_esc,
            "<<LOCATION>>": loc_esc,
            "<<SUMMARY>>": summary,
            "<<SKILLS>>": skills_block,
            "<<EXPERIENCE>>": experiences_section,
            "<<PROJECTS>>": projects_section,
            "<<EDUCATION>>": education_section,
        }

        replaced_count = 0
        for placeholder, val in replacements.items():
            if placeholder in text:
                text = text.replace(placeholder, val)
                replaced_count += 1

        # 2. If no direct placeholders, smartly replace sections (supports \begin{rSection}, \section, \cvsection)
        if replaced_count == 0:
            # Replace candidate name in \name{...}, \author{...}, or \Huge...
            text = re.sub(r'(\\name\{)[^}]*(\})', rf'\g<1>{name_esc}\g<2>', text, count=1)
            text = re.sub(r'(\\author\{)[^}]*(\})', rf'\g<1>{name_esc}\g<2>', text, count=1)
            text = re.sub(r'(\\Huge\s*(?:\\textbf)?\{)[^}]*(\})', rf'\g<1>{name_esc}\g<2>', text, count=1)

            # A. Match \begin{rSection}{TITLE} ... \end{rSection} (e.g. FAANGPath, Trey Hunner resume templates)
            rsec_map = [
                (r'(\\begin\{rSection\}\{(?i:Summary|Professional Summary)\}\s*)([\s\S]*?)(\\end\{rSection\})', rf'\g<1>\n\n{summary}\n\n\g<3>'),
                (r'(\\begin\{rSection\}\{(?i:Skills|Technical Skills|Competencies)\}\s*)([\s\S]*?)(\\end\{rSection\})', rf'\g<1>\n\n{skills_block}\n\n\g<3>'),
                (r'(\\begin\{rSection\}\{(?i:Experience|Work Experience|Professional Experience)\}\s*)([\s\S]*?)(\\end\{rSection\})', rf'\g<1>\n\n{experiences_section}\n\n\g<3>'),
                (r'(\\begin\{rSection\}\{(?i:Projects|Key Projects|Personal Projects)\}\s*)([\s\S]*?)(\\end\{rSection\})', rf'\g<1>\n\n{projects_section}\n\n\g<3>'),
                (r'(\\begin\{rSection\}\{(?i:Education|Academic Background)\}\s*)([\s\S]*?)(\\end\{rSection\})', rf'\g<1>\n\n{education_section}\n\n\g<3>'),
            ]
            for pattern, repl in rsec_map:
                if re.search(pattern, text):
                    text = re.sub(pattern, repl, text, count=1)

            # B. Match standard LaTeX \section blocks
            sec_map = [
                (r'(\\section\*?\{(?i:Professional Summary|Summary)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)', f"\\g<1>{summary}\n\n"),
                (r'(\\section\*?\{(?i:Skills|Technical Skills|Competencies|Technical Competencies)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)', f"\\g<1>{skills_block}\n\n"),
                (r'(\\section\*?\{(?i:Experience|Work Experience|Professional Experience)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)', f"\\g<1>{experiences_section}\n\n"),
                (r'(\\section\*?\{(?i:Projects|Key Projects|Personal Projects)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)', f"\\g<1>{projects_section}\n\n"),
                (r'(\\section\*?\{(?i:Education|Academic Background)\}\s*)([\s\S]*?)(?=\\section|\%---|\\end\{document\}|$)', f"\\g<1>{education_section}\n\n"),
            ]
            for pattern, repl in sec_map:
                if re.search(pattern, text):
                    text = re.sub(pattern, repl, text, count=1)

        # Sanitize \usepackage{hyperref} to self-contained shims if needed
        safe_href_shim = (
            "\\providecommand{\\href}[2]{\\underline{#2}}\n"
            "\\providecommand{\\url}[1]{\\texttt{#1}}\n"
            "\\providecommand{\\hypersetup}[1]{}\n"
        )
        if "\\usepackage{hyperref}" in text:
            text = text.replace("\\usepackage{hyperref}", safe_href_shim)

        return text

    def compile_pdf(
        self,
        tex_content: str,
        output_base_name: str,
        target_dir: Path,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Compiles LaTeX source code into PDF via pdflatex within an isolated temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy user custom template dependencies (.cls, .sty, images) into compilation workspace
            if user_id:
                tpl_dir = self.get_user_template_dir(user_id)
                if tpl_dir.exists():
                    for item in tpl_dir.iterdir():
                        if item.is_file() and item.name not in ["main.tex", "meta.json"]:
                            dest_file = tmp_path / item.name
                            shutil.copy2(item, dest_file)
                            # Make .cls self-contained if it imports hyperref/parskip
                            if item.suffix == ".cls":
                                try:
                                    cls_text = dest_file.read_text(encoding="utf-8")
                                    # Safe parskip replacement
                                    cls_text = cls_text.replace(
                                        r"\usepackage[parfill]{parskip}",
                                        r"\setlength{\parindent}{0pt}\setlength{\parskip}{0.5\baselineskip}",
                                    )
                                    # Safe hyperref replacement
                                    cls_text = cls_text.replace(
                                        r"\usepackage{hyperref}",
                                        r"\providecommand{\href}[2]{#2}\providecommand{\url}[1]{\texttt{#1}}\providecommand{\hypersetup}[1]{}",
                                    )
                                    cls_text = re.sub(r'\\hypersetup\{[^}]*\}', '', cls_text)
                                    dest_file.write_text(cls_text, encoding="utf-8")
                                except Exception:
                                    pass

            # Safe shims for tex_content
            cleaned_tex = tex_content
            if "\\usepackage{hyperref}" in cleaned_tex:
                cleaned_tex = cleaned_tex.replace(
                    r"\usepackage{hyperref}",
                    r"\providecommand{\href}[2]{\underline{#2}}\providecommand{\url}[1]{\texttt{#1}}\providecommand{\hypersetup}[1]{}"
                )

            tex_file = tmp_path / f"{output_base_name}.tex"
            tex_file.write_text(cleaned_tex, encoding="utf-8")

            # Run pdflatex safely with -halt-on-error and -disable-installer to NEVER hang
            cmd = [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-disable-installer",
                "-no-shell-escape",
                f"{output_base_name}.tex",
            ]

            process = subprocess.run(
                cmd,
                cwd=tmp_path,
                capture_output=True,
                text=True,
                timeout=20,
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

        # Render LaTeX using user's template if uploaded, otherwise system default
        tex_source = self.render_latex(
            candidate_name=user.full_name or "Candidate",
            candidate_email=user.email,
            phone=phone,
            location=location,
            content=resume.content or {},
            target_role=resume.target_role or "Software Engineer",
            user_id=user.id,
        )

        user_storage = self.get_user_artifact_dir(user.id)
        base_name = f"resume_v{resume.version_number}_job{resume.job_id}"

        # Compile PDF with user template support
        compile_result = self.compile_pdf(tex_source, base_name, user_storage, user_id=user.id)

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
