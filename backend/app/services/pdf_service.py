import re
from typing import Dict, List, Optional, Any, Set, Tuple
import fitz  # PyMuPDF
import pymupdf4llm
from app.services.ai.ollama_provider import ollama_provider
from app.services.skill_pipeline import skill_pipeline, appears_in_source as _appears_in_source


def clean_resume_markdown(text: str) -> str:
    """Converts Markdown text returned by PyMuPDF4LLM into clean plain resume text."""
    # Convert html line breaks to newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    # Remove html tags such as <u>, </u>
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    # Remove markdown table separator rows like |---|---|
    text = re.sub(r"^\s*\|[-:\s|]+\|\s*$", "", text, flags=re.MULTILINE)
    # Strip table pipes at line boundaries while preserving interior pipes
    text = re.sub(r"^\s*\|\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*\|\s*$", "", text, flags=re.MULTILINE)
    # Remove image tags
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    # [GitHub](url) -> GitHub
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # '## SKILLS' -> 'SKILLS'
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    # Page-break lines '-----'
    text = re.sub(r"^\s*-{3,}\s*$", "", text, flags=re.MULTILINE)
    # Bold and strikethrough markers
    text = text.replace("**", "").replace("__", "").replace("~~", "")
    # *italic* -> italic
    text = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)\*(?![\w*])", r"\1", text)
    # _italic_ -> italic
    text = re.sub(r"(?<![\w_])_(?!\s)([^_\n]+?)_(?![\w_])", r"\1", text)
    # Bullet symbols -> '- '
    text = re.sub(r"^\s*[•●▪◦*\ufffd]\s+", "- ", text, flags=re.MULTILINE)
    # Join hyphenated line breaks
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class PdfService:
    # Common section header patterns
    SECTION_PATTERNS = {
        "summary": r"^(?:professional\s+|executive\s+)?(?:summary|profile|about\s+me|objective)",
        "skills": r"^(?:technical\s+|core\s+)?(?:skills|competencies|technologies|tools|expertise)(?:\s*(?:&|and)\s*[\w\s]+)?",
        "experience": r"^(?:work\s+|professional\s+|relevant\s+)?(?:experience|employment|work\s+history|history)(?:\s*(?:&|and)\s*[\w\s]+)?",
        "projects": r"^(?:key\s+|personal\s+|academic\s+|technical\s+)?(?:projects|portfolio)(?:\s*(?:&|and)\s*[\w\s]+)?",
        "education": r"^(?:education|academic\s+background|academic\s+credentials|qualifications)(?:\s*(?:&|and)\s*[\w\s]+)?",
        "certifications": r"^(?:certifications|certificates|licenses|courses|awards|achievements)(?:\s*(?:&|and)\s*[\w\s]+)?",
    }

    # Known common technical skills mapped to canonical industry casing
    CANONICAL_TECH_SKILLS = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "react": "React",
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "node": "Node.js",
        "express": "Express",
        "sql": "SQL",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "docker": "Docker",
        "git": "Git",
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "GCP",
        "linux": "Linux",
        "html": "HTML",
        "css": "CSS",
        "tailwind": "Tailwind",
        "rest api": "REST API",
        "graphql": "GraphQL",
        "kubernetes": "Kubernetes",
        "redis": "Redis",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "c++": "C++",
        "java": "Java",
        "c#": "C#",
    }

    clean_resume_markdown = staticmethod(clean_resume_markdown)
    _appears_in_source = staticmethod(_appears_in_source)

    def _extract_plain(self, file_path: str) -> str:
        """The original plain implementation (page.get_text('text') per page, joined with '\n\n', stripped)."""
        doc = fitz.open(file_path)
        full_text = []
        for page in doc:
            text = page.get_text("text")
            if text:
                full_text.append(text)
        doc.close()
        return "\n\n".join(full_text).strip()

    def _extract_markdown(self, file_path: str) -> str:
        """pymupdf4llm.to_markdown(file_path, write_images=False) passed through clean_resume_markdown."""
        md_text = pymupdf4llm.to_markdown(file_path, write_images=False)
        return clean_resume_markdown(md_text)

    def extract_text_from_pdf_plain(self, file_path: str) -> str:
        """Public method returning plain text (used by the regex fallback and the debug script)."""
        try:
            return self._extract_plain(file_path)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Runs both plain and markdown extraction. It returns the markdown-cleaned text ONLY IF
        len(segment_sections(markdown_text)) >= len(segment_sections(plain_text)) AND the markdown text
        has at least 85% of the plain text's line count. Otherwise it returns the plain text.
        If markdown extraction raises, return plain. If both texts are empty, raise
        ValueError('No readable text found in this PDF. Scanned or image-only PDFs are not supported.').
        """
        plain_text = ""
        try:
            plain_text = self._extract_plain(file_path)
        except Exception:
            plain_text = ""

        md_text = ""
        try:
            md_text = self._extract_markdown(file_path)
        except Exception:
            md_text = ""

        if not plain_text and not md_text:
            raise ValueError("No readable text found in this PDF. Scanned or image-only PDFs are not supported.")

        if md_text and plain_text:
            sec_md = len(self.segment_sections(md_text))
            sec_plain = len(self.segment_sections(plain_text))
            lines_md = len(md_text.splitlines())
            lines_plain = len(plain_text.splitlines())
            if sec_md >= sec_plain and lines_md >= 0.85 * lines_plain:
                return md_text
            return plain_text

        return md_text if md_text else plain_text

    def extract_links_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extracts clickable link annotations from all pages of a PDF."""
        links: List[Dict[str, Any]] = []
        try:
            doc = fitz.open(file_path)
            for page_idx, page in enumerate(doc):
                for link in page.get_links():
                    uri = link.get("uri")
                    if uri:
                        rect = link.get("from")
                        rect_coords = [rect.x0, rect.y0, rect.x1, rect.y1] if rect else None
                        links.append({
                            "page": page_idx,
                            "uri": uri.strip(),
                            "rect": rect_coords,
                        })
            doc.close()
        except Exception:
            # Non-blocking if links cannot be inspected
            pass
        return links

    def segment_sections(self, raw_text: str) -> Dict[str, str]:
        """Segments raw resume text into logical sections based on headers."""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        sections: Dict[str, List[str]] = {}
        current_section = "header"
        sections[current_section] = []

        for line in lines:
            line_lower = line.lower()
            matched_header = None

            # Look for matches with known headers (short standalone line)
            if len(line.split()) <= 6:
                for section_name, pattern in self.SECTION_PATTERNS.items():
                    if re.match(pattern, line_lower):
                        matched_header = section_name
                        break

            if matched_header:
                current_section = matched_header
                if current_section not in sections:
                    sections[current_section] = []
            else:
                sections[current_section].append(line)

        return {k: "\n".join(v) for k, v in sections.items() if v}

    def detect_skills_deterministically(self, text: str) -> List[str]:
        """Detects presence of known tech skills in extracted text deterministically."""
        text_lower = text.lower()
        found_skills = []
        for skill_key, canonical_name in self.CANONICAL_TECH_SKILLS.items():
            pattern = rf"\b{re.escape(skill_key)}\b"
            if re.search(pattern, text_lower):
                found_skills.append(canonical_name)
        return sorted(list(set(found_skills)))

    # --- Comprehensive Structured Resume Extraction ---

    def _extract_personal_info(
        self,
        header_text: str,
        full_text: str,
        links: List[Dict[str, Any]],
    ) -> Dict[str, Optional[str]]:
        """Extracts candidate contact details, name, and profile URLs without hallucinations."""
        info: Dict[str, Optional[str]] = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
            "linkedin_url": None,
            "github_url": None,
            "portfolio_url": None,
        }

        # 1. Email extraction
        email_match = re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
            full_text,
        )
        if email_match:
            info["email"] = email_match.group(0).strip()
        else:
            for l in links:
                if l["uri"].startswith("mailto:"):
                    info["email"] = l["uri"].replace("mailto:", "").split("?")[0].strip()
                    break

        # 2. Phone extraction (Indian & US/Intl formats)
        phone_match = re.search(
            r"(?:(?:\+?91|0091)[\s().-]?)?(?:0[\s().-]?)?[6-9]\d{4}[\s.-]?\d{5}|(?:\+?1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}",
            full_text,
        )
        if phone_match:
            info["phone"] = phone_match.group(0).strip()

        # 3. LinkedIn URL (Link annotations first, then text regex)
        for l in links:
            uri = l["uri"]
            if "linkedin.com" in uri.lower():
                clean_url = uri.split("?")[0].rstrip("/")
                if "/in/" in clean_url or "/feed" in clean_url or "/company/" in clean_url:
                    info["linkedin_url"] = clean_url
                    break
        if not info["linkedin_url"]:
            li_match = re.search(
                r"https?://(?:www\.)?linkedin\.com/(?:in|feed|company)/[A-Za-z0-9_\-]+",
                full_text,
                re.IGNORECASE,
            )
            if li_match:
                info["linkedin_url"] = li_match.group(0).rstrip("/")

        # 4. GitHub URL (Link annotations first, then text regex)
        for l in links:
            uri = l["uri"]
            if "github.com" in uri.lower() and not uri.lower().endswith("github.com"):
                info["github_url"] = uri.split("?")[0].rstrip("/")
                break
        if not info["github_url"]:
            gh_match = re.search(
                r"https?://(?:www\.)?github\.com/[A-Za-z0-9_\-]+(?:/[A-Za-z0-9_\-]+)?",
                full_text,
                re.IGNORECASE,
            )
            if gh_match:
                info["github_url"] = gh_match.group(0).rstrip("/")

        # 5. Portfolio URL
        for l in links:
            uri = l["uri"]
            uri_lower = uri.lower()
            if (
                not uri_lower.startswith("mailto:")
                and "linkedin.com" not in uri_lower
                and "github.com" not in uri_lower
                and any(tld in uri_lower for tld in [".vercel.app", ".github.io", ".netlify.app", ".dev", ".me", ".io", "portfolio"])
            ):
                info["portfolio_url"] = uri.split("?")[0].rstrip("/")
                break

        # 6. Location (City, State / Country)
        header_lines = [line.strip() for line in header_text.splitlines() if line.strip()]
        for line in header_lines:
            loc_match = re.search(
                r"\b([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z\s]+))\b",
                line,
            )
            if loc_match:
                candidate_loc = loc_match.group(1).strip()
                # Exclude if it looks like an email or institution
                if "@" not in candidate_loc and len(candidate_loc.split()) <= 5:
                    info["location"] = candidate_loc
                    break

        # 7. Name from top header line
        for line in header_lines:
            clean_line = re.sub(r"[\-–|•·].*$", "", line).strip()
            # If line has no digits, no @, not too long, and has alphabetical characters
            if (
                clean_line
                and not re.search(r"\d", clean_line)
                and "@" not in clean_line
                and "http" not in clean_line.lower()
                and 2 <= len(clean_line.split()) <= 4
            ):
                info["name"] = clean_line
                break

        return info

    def _extract_education(self, edu_text: str) -> List[Dict[str, Any]]:
        """Extracts structured education items from the education section text."""
        items: List[Dict[str, Any]] = []
        if not edu_text:
            return items

        lines = [line.strip() for line in edu_text.splitlines() if line.strip()]
        degree_patterns = [
            r"\b(?:Bachelor|Master|Doctor|B\.?Tech|B\.?E\.?|B\.?Sc|M\.?Tech|M\.?S\.?|M\.?Sc|BCA|MCA|Ph\.?D|Diploma|High School)\b.*",
        ]
        date_pattern = r"\b(?:19|20)\d{2}(?:\s*[\-–to]+\s*(?:(?:19|20)\d{2}|Present|Current))?\b"
        grade_pattern = r"(?:CGPA|GPA|Percentage)?[:\s]*([0-9]+(?:\.[0-9]+)?(?:\s*/\s*[0-9]+(?:\.[0-9]+)?)?|\b[0-9]{2}%)"

        current_edu: Optional[Dict[str, Any]] = None

        for line in lines:
            has_degree = any(re.search(pat, line, re.IGNORECASE) for pat in degree_patterns)
            has_date = re.search(date_pattern, line, re.IGNORECASE)

            if has_degree or (has_date and not current_edu):
                if current_edu and current_edu.get("institution"):
                    items.append(current_edu)

                current_edu = {
                    "degree": line if has_degree else "Degree",
                    "institution": "",
                    "field_of_study": "",
                    "grade": "",
                    "start_date": "",
                    "end_date": "",
                }

                # Extract date if present on degree line
                if has_date:
                    date_str = has_date.group(0).strip()
                    parts = re.split(r"[\-–to]+", date_str)
                    if len(parts) == 2:
                        current_edu["start_date"] = parts[0].strip()
                        current_edu["end_date"] = parts[1].strip()
                    else:
                        current_edu["end_date"] = parts[0].strip()
                    # Strip date from degree text
                    current_edu["degree"] = re.sub(date_pattern, "", current_edu["degree"], flags=re.IGNORECASE).strip(" -–|,")
            elif current_edu:
                # Check for grade/CGPA
                grade_match = re.search(grade_pattern, line, re.IGNORECASE)
                if grade_match and ("cgpa" in line.lower() or "gpa" in line.lower() or "%" in line):
                    current_edu["grade"] = line.strip(" -–|,")
                elif not current_edu["institution"]:
                    # Likely college/institution name
                    # Clean date if on institution line
                    if has_date and not current_edu["end_date"]:
                        date_str = has_date.group(0).strip()
                        parts = re.split(r"[\-–to]+", date_str)
                        current_edu["end_date"] = parts[-1].strip()
                        line = re.sub(date_pattern, "", line, flags=re.IGNORECASE).strip(" -–|,")
                    current_edu["institution"] = line

        if current_edu and (current_edu.get("institution") or current_edu.get("degree")):
            items.append(current_edu)

        return items

    GROUNDING_STOPWORDS = {
        "and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "with", "of", "by", "as",
        "is", "was", "were", "using", "built", "developed", "managed", "worked", "created"
    }

    def _clean_tokens(self, text: str) -> Set[str]:
        words = re.findall(r"\b[a-zA-Z0-9]{3,}\b", (text or "").lower())
        return {w for w in words if w not in self.GROUNDING_STOPWORDS}

    def _extract_experience(self, exp_text: str) -> List[Dict[str, Any]]:
        """Extracts structured work experience items, supporting multi-roles, wrapped bullets, location, and dates."""
        items: List[Dict[str, Any]] = []
        if not exp_text:
            return items

        lines = [line.strip() for line in exp_text.splitlines() if line.strip()]
        month_name = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        date_point = rf"(?:{month_name}\.?\s*)?(?:19|20)\d{{2}}"
        date_end = rf"(?:{date_point}|Present|Current|Ongoing)"
        date_range_pattern = rf"\b{date_point}\s*[\-–—to/]+\s*{date_end}\b"
        single_date_pattern = rf"\b{date_point}\b"

        current_exp: Optional[Dict[str, Any]] = None
        last_company: str = ""

        for line in lines:
            is_bullet = bool(re.match(r"^[\-•*–·▪o]\s+", line)) or line.startswith(("-", "•", "*", "–", "·", "▪"))
            range_match = re.search(date_range_pattern, line, re.IGNORECASE)
            single_match = re.search(single_date_pattern, line, re.IGNORECASE)
            date_match = range_match or single_match

            # Check if this line is an experience entry header (has date and not a bullet point)
            if date_match and not is_bullet:
                if current_exp and (current_exp.get("company") or current_exp.get("title")):
                    items.append(current_exp)

                date_str = date_match.group(0).strip()
                date_parts = re.split(r"[\-–—to/]+", date_str)
                start_date = date_parts[0].strip() if len(date_parts) > 1 else ""
                end_date = date_parts[1].strip() if len(date_parts) > 1 else date_parts[0].strip()
                is_curr = bool(re.search(r"\b(?:Present|Current|Ongoing)\b", line, re.IGNORECASE))

                header_no_date = re.sub(date_range_pattern, "", line, flags=re.IGNORECASE)
                header_no_date = re.sub(single_date_pattern, "", header_no_date, flags=re.IGNORECASE).strip(" -–—|,")
                parts = [p.strip() for p in re.split(r"[\-–—|]", header_no_date) if p.strip()]

                company = ""
                title = ""
                location = ""

                loc_paren = re.search(r"\(([^)]+)\)", header_no_date)
                if loc_paren and ("," in loc_paren.group(1) or any(w in loc_paren.group(1).lower() for w in ["remote", "india", "usa", "uk"])):
                    location = loc_paren.group(1).strip()
                    header_no_date = re.sub(r"\([^)]+\)", "", header_no_date).strip(" -–—|,")
                    parts = [p.strip() for p in re.split(r"[\-–—|]", header_no_date) if p.strip()]

                if len(parts) >= 2:
                    role_keywords = ["engineer", "developer", "lead", "architect", "intern", "manager", "analyst", "consultant", "associate", "specialist"]
                    p0_is_role = any(rk in parts[0].lower() for rk in role_keywords)
                    p1_is_role = any(rk in parts[1].lower() for rk in role_keywords)
                    if p0_is_role and not p1_is_role:
                        title, company = parts[0], parts[1]
                    else:
                        company, title = parts[0], parts[1]
                elif len(parts) == 1:
                    role_keywords = ["engineer", "developer", "lead", "architect", "intern", "manager", "analyst", "consultant", "associate", "specialist"]
                    if any(rk in parts[0].lower() for rk in role_keywords):
                        title = parts[0]
                        company = last_company or "Organization"
                    else:
                        company = parts[0]
                        title = "Software Engineer"
                else:
                    company = last_company or "Organization"
                    title = "Role"

                if company and company != "Organization":
                    last_company = company

                current_exp = {
                    "company": company,
                    "title": title,
                    "location": location,
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_current": is_curr,
                    "bullets": [],
                }
            elif current_exp:
                # If current_exp needs company and this line provides Company | Location (e.g. Title on line 1, Company on line 2)
                if (not current_exp["company"] or current_exp["company"] == "Organization") and not is_bullet and not date_match and len(line.split()) <= 6:
                    line_parts = [p.strip() for p in re.split(r"[\-–—|]", line) if p.strip()]
                    if len(line_parts) >= 2:
                        current_exp["company"] = line_parts[0]
                        current_exp["location"] = line_parts[1]
                        last_company = current_exp["company"]
                        continue
                    elif len(line_parts) == 1 and not line.endswith("."):
                        current_exp["company"] = line_parts[0]
                        last_company = current_exp["company"]
                        continue

                if is_bullet:
                    bullet_text = re.sub(r"^[\-•*–·▪o\s]+", "", line).strip()
                    if bullet_text:
                        current_exp["bullets"].append(bullet_text)
                else:
                    loc_match = re.search(r"\b([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z\s]+))\b", line)
                    if (loc_match or any(k in line.lower() for k in ["remote", "hybrid", "on-site"])) and not current_exp["location"] and len(line.split()) <= 4:
                        current_exp["location"] = line.strip(" -–|,()")
                    elif current_exp["bullets"]:
                        current_exp["bullets"][-1] = f"{current_exp['bullets'][-1]} {line.strip()}"
                    elif len(line.split()) > 4:
                        current_exp["bullets"].append(line.strip())
            else:
                if not is_bullet and len(line.split()) <= 6 and not any(c in line for c in ["@", "http", "www."]):
                    last_company = line.strip(" -–|,()")

        if current_exp and (current_exp.get("company") or current_exp.get("title")):
            items.append(current_exp)

        return items

    def _extract_projects(
        self,
        proj_text: str,
        links: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extracts structured project records, technologies, dates, and accurately assigned links."""
        items: List[Dict[str, Any]] = []
        if not proj_text:
            return items

        lines = [line.strip() for line in proj_text.splitlines() if line.strip()]
        if not lines:
            return items

        link_badge_words = {
            "live", "github", "demo", "code", "website", "site", "link",
            "preview", "app", "video", "paper", "view", "pdf", "repo", "source"
        }

        action_verbs = {
            "developed", "implemented", "built", "created", "designed", "engineered",
            "led", "configured", "maintained", "architected", "automated", "integrated",
            "spearheaded", "collaborated", "resolved", "optimized", "utilized", "conducted",
            "analyzed", "deployed", "established", "improved", "enhanced", "reduced",
            "increased", "streamlined", "managed", "delivered", "programmed", "trained",
            "orchestrated", "refactored", "authored", "executed", "formulated", "researched"
        }

        month_name = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        date_point = rf"(?:{month_name}\.?\s*)?(?:19|20)\d{{2}}"
        date_end = rf"(?:{date_point}|Present|Current|Ongoing)"
        date_range_pattern = rf"\b{date_point}\s*(?:[\-–—/]+|\bto\b)\s*{date_end}\b"
        single_date_pattern = rf"\b(?:{month_name}\.?\s+)?(?:19|20)\d{{2}}\b"

        def is_bullet_line(s: str) -> bool:
            if not s:
                return False
            if s[0] in ["•", "·", "▪"]:
                return True
            if re.match(r"^[\-*–o]\s+", s):
                return True
            return False

        def is_date_only_line(s: str) -> bool:
            if not s:
                return False
            s_clean = s.strip()
            s_no_date = re.sub(date_range_pattern, "", s_clean, flags=re.IGNORECASE)
            s_no_date = re.sub(single_date_pattern, "", s_no_date, flags=re.IGNORECASE)
            rem = re.sub(r"[\s\-–—/|(),\.]", "", s_no_date)
            if len(rem) == 0 and (
                re.search(date_range_pattern, s_clean, re.IGNORECASE)
                or re.search(single_date_pattern, s_clean, re.IGNORECASE)
                or s_clean.lower() in ["present", "current", "ongoing"]
            ):
                return True
            return False

        def is_tech_header_or_list(s: str) -> bool:
            if not s:
                return False
            s_lower = s.lower().strip()
            if any(s_lower.startswith(p) for p in [
                "technologies:", "tech stack:", "tools:", "built with:", "stack:",
                "technologies used:", "key technologies:", "tools used:", "environment:"
            ]):
                return True
            if "," in s and not is_bullet_line(s):
                parts = [p.strip() for p in s.split(",") if p.strip()]
                if 2 <= len(parts) <= 15:
                    if all(len(p.split()) <= 4 and not p.endswith(".") for p in parts):
                        first_word = parts[0].split()[0].lower() if parts[0].split() else ""
                        if first_word not in action_verbs:
                            return True
            return False

        def parse_technologies_line(s: str) -> List[str]:
            s_clean = re.sub(
                r"^(?:technologies(?: used)?|tech stack|tools(?: used)?|built with|stack|environment|key technologies):\s*",
                "",
                s,
                flags=re.IGNORECASE,
            ).strip()
            return [t.strip(" .;") for t in s_clean.split(",") if t.strip(" .;")]

        def parse_date_str(d_str: str) -> Tuple[str, str]:
            d_clean = d_str.strip()
            if re.search(date_range_pattern, d_clean, re.IGNORECASE):
                parts = re.split(r"\s*(?:[\-–—/]+|\bto\b)\s*", d_clean, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    return parts[0].strip(), parts[1].strip()
                elif len(parts) == 1:
                    return "", parts[0].strip()
            m = re.search(single_date_pattern, d_clean, re.IGNORECASE)
            if m:
                return "", m.group(0).strip()
            return "", d_clean

        def extract_tech_and_badges_from_title(title_candidate: str) -> Tuple[str, List[str]]:
            techs: List[str] = []
            clean_title = title_candidate

            brackets = re.findall(r"\[(.*?)\]", clean_title)
            for b in brackets:
                b_clean = b.strip()
                if b_clean.lower() in link_badge_words:
                    clean_title = clean_title.replace(f"[{b}]", "").strip()
                elif "," in b_clean or any(k in b_clean.lower() for k in ["python", "react", "java", "c++", "node", "sql", "aws", "docker"]):
                    techs.extend([t.strip() for t in b_clean.split(",") if t.strip()])
                    clean_title = clean_title.replace(f"[{b}]", "").strip()
                else:
                    words = [w.lower() for w in re.findall(r"\w+", b_clean)]
                    if words and all(w in link_badge_words for w in words):
                        clean_title = clean_title.replace(f"[{b}]", "").strip()

            parens = re.findall(r"\((.*?)\)", clean_title)
            for p in parens:
                p_clean = p.strip()
                if p_clean.lower() in link_badge_words:
                    clean_title = clean_title.replace(f"({p})", "").strip()
                elif "," in p_clean or any(k in p_clean.lower() for k in ["python", "react", "java", "c++", "node", "sql", "aws", "docker"]):
                    techs.extend([t.strip() for t in p_clean.split(",") if t.strip()])
                    clean_title = clean_title.replace(f"({p})", "").strip()
                else:
                    words = [w.lower() for w in re.findall(r"\w+", p_clean)]
                    if words and all(w in link_badge_words for w in words):
                        clean_title = clean_title.replace(f"({p})", "").strip()

            clean_title = re.sub(r"\s+", " ", clean_title).strip(" -–—|,")
            return clean_title, techs

        current_proj: Optional[Dict[str, Any]] = None
        assigned_uris: Set[str] = set()

        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]

            # 1. Date-only line check
            if is_date_only_line(line):
                if current_proj is not None and (not current_proj["start_date"] and not current_proj["end_date"]):
                    s_date, e_date = parse_date_str(line)
                    current_proj["start_date"] = s_date
                    current_proj["end_date"] = e_date
                i += 1
                continue

            # 2. Technology line check
            if is_tech_header_or_list(line):
                if current_proj is not None and (not current_proj["technologies"] or any(line.lower().startswith(p) for p in ["technologies:", "tech stack:", "tools:", "built with:", "stack:"])):
                    current_proj["technologies"] = parse_technologies_line(line)
                i += 1
                continue

            # 3. Bullet line check
            if is_bullet_line(line):
                bullet_text = re.sub(r"^[\-•*–·▪o\s]+", "", line).strip()
                if bullet_text and not bullet_text.startswith("http"):
                    if current_proj is None:
                        current_proj = {
                            "title": "Project",
                            "technologies": [],
                            "description": "",
                            "bullets": [],
                            "github_url": "",
                            "live_url": "",
                            "start_date": "",
                            "end_date": "",
                        }
                    current_proj["bullets"].append(bullet_text)
                i += 1
                continue

            # 4. URL line check
            if re.match(r"^https?://", line, re.IGNORECASE) or line.lower().startswith("github.com"):
                if current_proj is not None:
                    if "github.com" in line.lower() and not current_proj["github_url"]:
                        current_proj["github_url"] = line.strip()
                        assigned_uris.add(line.strip().lower())
                    elif not current_proj["live_url"]:
                        current_proj["live_url"] = line.strip()
                        assigned_uris.add(line.strip().lower())
                i += 1
                continue

            # 5. Project title or bullet/description continuation
            first_word = line.split()[0].lower() if line.split() else ""
            is_action_verb = first_word in action_verbs
            ends_in_period = line.endswith(".")
            word_count = len(line.split())

            next_line = lines[i + 1] if i + 1 < n else ""
            next_is_date = is_date_only_line(next_line) if next_line else False
            next_is_tech = is_tech_header_or_list(next_line) if next_line else False
            next_is_bullet = is_bullet_line(next_line) if next_line else False
            next_is_url = bool(re.match(r"^https?://", next_line, re.IGNORECASE) or next_line.lower().startswith("github.com")) if next_line else False

            has_pipe = "|" in line
            has_badge = any(f"[{w}]" in line.lower() or f"({w})" in line.lower() for w in link_badge_words)
            has_dash_sep = " — " in line or " – " in line
            has_date = bool(re.search(date_range_pattern, line, re.IGNORECASE))

            is_title = (
                not is_action_verb
                and not ends_in_period
                and word_count <= 20
                and (
                    next_is_date
                    or next_is_tech
                    or next_is_url
                    or has_pipe
                    or has_badge
                    or has_date
                    or (has_dash_sep and word_count <= 15)
                    or (current_proj is None and word_count <= 12)
                    or (next_is_bullet and (current_proj is None or len(current_proj["bullets"]) > 0 or current_proj["description"]))
                )
            )

            if is_title:
                if current_proj and (current_proj.get("title") or current_proj.get("bullets")):
                    items.append(current_proj)

                start_date = ""
                end_date = ""

                date_match = re.search(date_range_pattern, line, re.IGNORECASE)
                if date_match:
                    start_date, end_date = parse_date_str(date_match.group(0))
                    line = re.sub(date_range_pattern, "", line, flags=re.IGNORECASE)
                else:
                    single_match = re.search(single_date_pattern, line, re.IGNORECASE)
                    if single_match and ("|" in line or " - " in line or " — " in line):
                        start_date, end_date = parse_date_str(single_match.group(0))
                        line = re.sub(single_date_pattern, "", line, flags=re.IGNORECASE)

                clean_title, title_techs = extract_tech_and_badges_from_title(line)

                if "|" in clean_title:
                    p_parts = [p.strip() for p in clean_title.split("|") if p.strip()]
                    clean_title = p_parts[0]
                    for extra in p_parts[1:]:
                        if "," in extra:
                            title_techs.extend([t.strip() for t in extra.split(",") if t.strip()])
                        elif len(extra.split()) <= 3 and not start_date and not end_date:
                            s_d, e_d = parse_date_str(extra)
                            if e_d:
                                start_date, end_date = s_d, e_d

                current_proj = {
                    "title": clean_title or "Project",
                    "technologies": title_techs,
                    "description": "",
                    "bullets": [],
                    "github_url": "",
                    "live_url": "",
                    "start_date": start_date,
                    "end_date": end_date,
                }
                i += 1
                continue

            # Non-title line: bullet continuation or description
            if current_proj and current_proj["bullets"]:
                current_proj["bullets"][-1] = f"{current_proj['bullets'][-1]} {line}".strip()
            elif current_proj:
                if not current_proj["description"]:
                    current_proj["description"] = line.strip()
                else:
                    current_proj["description"] = f"{current_proj['description']} {line}".strip()
            i += 1

        if current_proj and (current_proj.get("title") or current_proj.get("bullets")):
            items.append(current_proj)

        # Map PDF links to projects by title / keyword match
        for p in items:
            p_title_words = [w.lower() for w in re.findall(r"\w+", p["title"]) if len(w) > 3]
            for l in links:
                uri = l.get("uri", "")
                uri_lower = uri.lower()
                if uri_lower in assigned_uris:
                    continue

                if "github.com" in uri_lower and not p["github_url"]:
                    path_parts = [part for part in uri_lower.split("github.com/")[-1].split("?")[0].split("/") if part]
                    is_personal_profile = len(path_parts) <= 1
                    matches_title = any(w in uri_lower for w in p_title_words)

                    if matches_title or (not is_personal_profile and len(items) == 1):
                        p["github_url"] = uri
                        assigned_uris.add(uri_lower)
                        if p["github_url"] and p["live_url"]:
                            break
                elif not p["live_url"] and not uri_lower.startswith("mailto:") and "linkedin.com" not in uri_lower and "github.com" not in uri_lower:
                    matches_title = any(w in uri_lower for w in p_title_words)
                    if matches_title or len(items) == 1:
                        p["live_url"] = uri
                        assigned_uris.add(uri_lower)
                        if p["github_url"] and p["live_url"]:
                            break

        return items

    def _extract_certifications(
        self,
        cert_text: str,
        links: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extracts structured certifications, issuer, dates, credential ID, and verification URLs."""
        items: List[Dict[str, Any]] = []
        if not cert_text:
            return items

        lines = [line.strip() for line in cert_text.splitlines() if line.strip()]
        date_pattern = r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*(?:19|20)\d{2}\b"
        assigned_cert_uris: Set[str] = set()

        for line in lines:
            clean_line = re.sub(r"^[\-•*–·▪o\s]+", "", line).strip()
            if not clean_line:
                continue

            if clean_line.startswith("http") and items:
                if not items[-1].get("credential_url"):
                    items[-1]["credential_url"] = clean_line
                    assigned_cert_uris.add(clean_line.lower())
                continue

            # Check if this line is a subline with Credential ID for the active certificate
            if items and any(clean_line.lower().startswith(p) for p in ["credential id", "credential:", "license:", "id:", "cert id"]):
                id_m = re.search(r"(?:credential\s*id|license|cert\s*id|id)\s*[:#]\s*([A-Za-z0-9_\-]+)", clean_line, re.IGNORECASE)
                if id_m:
                    items[-1]["credential_id"] = id_m.group(1).strip()
                    continue

            cred_id = ""
            cred_id_match = re.search(r"(?:Credential\s*ID|License|Cert(?:ificate)?\s*(?:#|No\.?|ID))\s*[:#]\s*([A-Za-z0-9_\-]+)", clean_line, re.IGNORECASE)
            if cred_id_match:
                cred_id = cred_id_match.group(1).strip()
                clean_line = re.sub(r"(?:Credential\s*ID|License|Cert(?:ificate)?\s*(?:#|No\.?|ID))\s*[:#]\s*[A-Za-z0-9_\-]+", "", clean_line, flags=re.IGNORECASE).strip(" -–—|,")

            date_match = re.search(date_pattern, clean_line, re.IGNORECASE)
            issue_date = date_match.group(0).strip() if date_match else ""
            if date_match:
                clean_line = re.sub(date_pattern, "", clean_line, flags=re.IGNORECASE).strip(" -–—|,")

            parts = [p.strip() for p in re.split(r"[\-–—|]", clean_line) if p.strip()]
            name = clean_line
            issuer = ""

            known_issuers = ["Amazon Web Services", "AWS", "Google Cloud", "Google", "Microsoft", "Azure", "Coursera", "Udemy", "edX", "CompTIA", "Cisco", "Oracle", "Meta", "Stanford", "Harvard", "FreeCodeCamp", "HackerRank"]

            if len(parts) >= 2:
                name = parts[0]
                issuer = parts[1]
            else:
                for ki in known_issuers:
                    if ki.lower() in clean_line.lower():
                        issuer = ki
                        break

            cred_url = ""
            name_words = [w.lower() for w in re.findall(r"\w+", name) if len(w) > 3]
            for l in links:
                uri = l.get("uri", "")
                uri_lower = uri.lower()
                if uri_lower in assigned_cert_uris:
                    continue
                # Exclude root profile or repository URLs
                if uri_lower.startswith("mailto:") or "linkedin.com" in uri_lower or "github.com" in uri_lower:
                    continue

                matches_cert = any(w in uri_lower for w in name_words) or any(k in uri_lower for k in ["verify", "verification", "credential", "certificate", "badge", "cred-"])
                if matches_cert or len(items) == 0:
                    cred_url = uri
                    assigned_cert_uris.add(uri_lower)
                    break

            items.append({
                "name": name,
                "issuer": issuer,
                "issue_date": issue_date,
                "expiration_date": "",
                "credential_id": cred_id,
                "credential_url": cred_url,
            })

        return items
    def validate_and_ground_personal_info(
        self,
        info: Dict[str, Any],
        source_text: str,
        regex_info: Dict[str, Any],
    ) -> Dict[str, Optional[str]]:
        """Strictly validates LLM-extracted personal info against source text, applying regex overrides."""
        grounded: Dict[str, Optional[str]] = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
            "headline": None,
            "linkedin_url": None,
            "github_url": None,
            "portfolio_url": None,
        }

        # Name
        name_val = info.get("name")
        if name_val and _appears_in_source(name_val, source_text):
            grounded["name"] = str(name_val).strip()

        # Location
        loc_val = info.get("location")
        if loc_val and _appears_in_source(loc_val, source_text):
            grounded["location"] = str(loc_val).strip()

        # Headline
        hl_val = info.get("headline")
        if hl_val and _appears_in_source(hl_val, source_text):
            grounded["headline"] = str(hl_val).strip()

        # Portfolio URL
        port_val = info.get("portfolio_url")
        if port_val and _appears_in_source(port_val, source_text):
            grounded["portfolio_url"] = str(port_val).strip()

        # Email, phone, github, linkedin: regex value wins over LLM value
        for key in ["email", "phone", "github_url", "linkedin_url"]:
            reg_val = regex_info.get(key)
            llm_val = info.get(key)
            if reg_val:
                grounded[key] = reg_val
            elif llm_val and _appears_in_source(llm_val, source_text):
                grounded[key] = str(llm_val).strip()

        return grounded

    def validate_and_ground_education(
        self, items: List[Dict[str, Any]], source_text: str
    ) -> List[Dict[str, Any]]:
        """Strictly validates LLM-extracted education items against source text."""
        grounded: List[Dict[str, Any]] = []
        for it in items:
            inst = str(it.get("institution") or "").strip()
            deg = str(it.get("degree") or "").strip()
            if not (_appears_in_source(inst, source_text) or _appears_in_source(deg, source_text)):
                continue

            field = it.get("field_of_study")
            if field and not _appears_in_source(field, source_text):
                field = None

            grade = it.get("grade")
            if grade and not _appears_in_source(grade, source_text):
                grade = None

            grounded.append({
                "institution": inst,
                "degree": deg,
                "field_of_study": field,
                "grade": grade,
                "start_date": it.get("start_date") or "",
                "end_date": it.get("end_date") or "",
            })
        return grounded

    def validate_and_ground_experience(
        self, items: List[Dict[str, Any]], source_text: str
    ) -> List[Dict[str, Any]]:
        """Strictly validates LLM-extracted experience against raw text to prevent hallucinations."""
        if not items or not source_text:
            return []
        grounded: List[Dict[str, Any]] = []

        for it in items:
            company = str(it.get("company") or "").strip()
            title = str(it.get("title") or "").strip()
            if not (_appears_in_source(company, source_text) or _appears_in_source(title, source_text)):
                continue

            valid_bullets = []
            for b in it.get("bullets") or []:
                b_str = str(b).strip()
                if b_str and _appears_in_source(b_str, source_text):
                    valid_bullets.append(b_str)

            desc = it.get("description") or ""
            if desc and not _appears_in_source(desc, source_text):
                desc = ""

            grounded.append({
                "company": company,
                "title": title,
                "location": it.get("location") or "",
                "start_date": it.get("start_date") or "",
                "end_date": it.get("end_date") or "",
                "is_current": bool(it.get("is_current", False)),
                "description": desc,
                "bullets": valid_bullets,
            })

        return grounded

    def validate_and_ground_projects(
        self, items: List[Dict[str, Any]], source_text: str, doc_links: List[str]
    ) -> List[Dict[str, Any]]:
        """Strictly validates LLM-extracted projects and URLs against source text and PDF links."""
        if not items or not source_text:
            return []
        doc_links_lower = {l.lower().strip() for l in doc_links}
        grounded: List[Dict[str, Any]] = []

        for p in items:
            title = str(p.get("title") or "").strip()
            if not title or not _appears_in_source(title, source_text):
                continue

            gh_url = str(p.get("github_url") or p.get("url") or "").strip()
            if gh_url and gh_url.lower() not in doc_links_lower and not _appears_in_source(gh_url, source_text):
                gh_url = ""

            live_url = str(p.get("live_url") or "").strip()
            if live_url and live_url.lower() not in doc_links_lower and not _appears_in_source(live_url, source_text):
                live_url = ""

            valid_bullets = []
            for b in p.get("bullets") or []:
                b_str = str(b).strip()
                if b_str and _appears_in_source(b_str, source_text):
                    valid_bullets.append(b_str)

            valid_techs = []
            for t in p.get("technologies") or []:
                t_str = str(t).strip()
                if t_str and _appears_in_source(t_str, source_text):
                    valid_techs.append(t_str)

            desc = p.get("description") or ""
            if desc and not _appears_in_source(desc, source_text):
                desc = ""

            grounded.append({
                "title": title,
                "role": p.get("role") or "",
                "technologies": valid_techs,
                "description": desc,
                "bullets": valid_bullets,
                "url": gh_url or live_url,
                "github_url": gh_url,
                "live_url": live_url,
                "start_date": p.get("start_date") or "",
                "end_date": p.get("end_date") or "",
            })

        return grounded

    def validate_and_ground_certifications(
        self, items: List[Dict[str, Any]], source_text: str, doc_links: List[str]
    ) -> List[Dict[str, Any]]:
        """Strictly validates LLM-extracted certifications against source text and PDF links."""
        if not items or not source_text:
            return []
        doc_links_lower = {l.lower().strip() for l in doc_links}
        grounded: List[Dict[str, Any]] = []

        for c in items:
            name = str(c.get("name") or "").strip()
            if not name or not _appears_in_source(name, source_text):
                continue

            cred_url = str(c.get("credential_url") or "").strip()
            if cred_url and cred_url.lower() not in doc_links_lower and not _appears_in_source(cred_url, source_text):
                cred_url = ""

            grounded.append({
                "name": name,
                "issuer": c.get("issuer") or "",
                "issue_date": c.get("issue_date") or "",
                "expiration_date": c.get("expiration_date") or "",
                "credential_id": c.get("credential_id") or "",
                "credential_url": cred_url,
            })

        return grounded

    def extract_full_resume_data(
        self,
        file_path: str,
        raw_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extracts complete candidate profile and career history deterministically from PDF."""
        if not raw_text:
            raw_text = self.extract_text_from_pdf(file_path)

        links = self.extract_links_from_pdf(file_path)
        sections = self.segment_sections(raw_text)

        personal_info = self._extract_personal_info(
            header_text=sections.get("header", ""),
            full_text=raw_text,
            links=links,
        )

        detected_skills = self.detect_skills_deterministically(raw_text)

        education = self._extract_education(sections.get("education", ""))
        experience = self._extract_experience(sections.get("experience", ""))
        projects = self._extract_projects(sections.get("projects", ""), links=links)
        certifications = self._extract_certifications(sections.get("certifications", ""), links=links)

        return {
            "personal_info": personal_info,
            "skills": detected_skills,
            "summary": sections.get("summary", "").strip(),
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications,
            "sections_found": list(sections.keys()),
        }

    async def extract_full_resume_data_hybrid(
        self,
        file_path: str,
        raw_text: Optional[str] = None,
        plain_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """LLM-first extraction pipeline with strict source grounding and deterministic regex fallback."""
        if not plain_text:
            plain_text = self.extract_text_from_pdf_plain(file_path)
        if not raw_text:
            raw_text = self.extract_text_from_pdf(file_path)

        links = self.extract_links_from_pdf(file_path)
        doc_links = [l["uri"] for l in links if l.get("uri")]

        # Run regex parsers on plain text for fallback and link enrichment
        regex_sections = self.segment_sections(plain_text)
        regex_personal = self._extract_personal_info(
            header_text=regex_sections.get("header", ""),
            full_text=plain_text,
            links=links,
        )
        regex_education = self._extract_education(regex_sections.get("education", ""))
        regex_experience = self._extract_experience(regex_sections.get("experience", ""))
        regex_projects = self._extract_projects(regex_sections.get("projects", ""), links=links)
        regex_certifications = self._extract_certifications(regex_sections.get("certifications", ""), links=links)
        regex_skills = self.detect_skills_deterministically(plain_text)

        # Check Ollama availability
        ollama_ok = False
        try:
            ollama_ok = await ollama_provider.is_available()
        except Exception:
            ollama_ok = False

        llm_data = None
        if ollama_ok:
            try:
                llm_data = await ollama_provider.extract_full_resume_structure(raw_text, doc_links)
            except Exception:
                llm_data = None

        if llm_data:
            # 1. Personal Info
            llm_p = llm_data.personal_info.model_dump() if llm_data.personal_info else {}
            grounded_p = self.validate_and_ground_personal_info(llm_p, raw_text, regex_personal)
            if not grounded_p.get("name") and not any(grounded_p.values()):
                final_personal = regex_personal
            else:
                if not grounded_p.get("name") and regex_personal.get("name"):
                    grounded_p["name"] = regex_personal["name"]
                final_personal = grounded_p

            # 2. Summary
            final_summary = llm_data.summary.strip() if llm_data.summary and llm_data.summary.strip() else regex_sections.get("summary", "").strip()

            # 3. Education
            llm_edus = [it.model_dump() for it in llm_data.education]
            grounded_edus = self.validate_and_ground_education(llm_edus, raw_text)
            final_education = grounded_edus if len(grounded_edus) > 0 else regex_education

            # 4. Experience
            llm_exps = [it.model_dump() for it in llm_data.experience]
            grounded_exps = self.validate_and_ground_experience(llm_exps, raw_text)
            final_experience = grounded_exps if len(grounded_exps) > 0 else regex_experience

            # 5. Projects
            llm_projs = [it.model_dump() for it in llm_data.projects]
            grounded_projs = self.validate_and_ground_projects(llm_projs, raw_text, doc_links)
            final_projects = grounded_projs if len(grounded_projs) > 0 else regex_projects

            # 6. Certifications
            llm_certs = [it.model_dump() for it in llm_data.certifications]
            grounded_certs = self.validate_and_ground_certifications(llm_certs, raw_text, doc_links)
            final_certifications = grounded_certs if len(grounded_certs) > 0 else regex_certifications
        else:
            final_personal = regex_personal
            final_summary = regex_sections.get("summary", "").strip()
            final_education = regex_education
            final_experience = regex_experience
            final_projects = regex_projects
            final_certifications = regex_certifications

        # Skills Pipeline
        final_skills: List[Dict[str, Optional[str]]] = []
        if ollama_ok:
            try:
                final_skills = await skill_pipeline.extract_and_categorize(raw_text)
            except Exception:
                final_skills = []

        if not final_skills:
            final_skills = [{"name": s, "category": None} for s in regex_skills]

        return {
            "personal_info": final_personal,
            "skills": final_skills,
            "summary": final_summary,
            "education": final_education,
            "experience": final_experience,
            "projects": final_projects,
            "certifications": final_certifications,
            "sections_found": list(regex_sections.keys()),
        }


pdf_service = PdfService()
