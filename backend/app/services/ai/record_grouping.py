"""Deterministic and Layout-Aware Record Grouping Engine for Master Resume Extraction."""

import logging
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple, Set

logger = logging.getLogger(__name__)

# Action verbs commonly beginning bullet points in resumes
ACTION_VERBS: Set[str] = {
    "developed", "implemented", "built", "created", "designed", "engineered",
    "led", "configured", "maintained", "architected", "automated", "integrated",
    "spearheaded", "collaborated", "resolved", "optimized", "utilized", "conducted",
    "analyzed", "deployed", "established", "improved", "enhanced", "reduced",
    "increased", "streamlined", "managed", "delivered", "programmed", "trained",
    "orchestrated", "refactored", "authored", "executed", "formulated", "researched",
    "achieved", "assisted", "coordinated", "generated", "launched", "monitored",
    "produced", "secured", "supervised", "tested", "wrote", "overhauled", "coached",
}

# Canonical section heading keywords to distinguish from candidate names and bullet points
KNOWN_SECTION_HEADINGS: Set[str] = {
    "summary", "professional summary", "executive summary", "profile", "about me", "objective",
    "skills", "technical skills", "core competencies", "technologies", "tools", "technical exposure",
    "experience", "work experience", "professional experience", "employment history", "employment", "research experience",
    "projects", "key projects", "personal projects", "academic projects", "technical projects", "portfolio",
    "education", "academic background", "academic credentials", "qualifications", "academic history",
    "certifications", "certificates", "licenses", "courses",
    "achievements", "awards", "honors", "key achievements",
    "volunteering", "volunteering & community outreach", "community outreach", "community service",
    "publications", "patents", "languages", "interests", "hobbies", "activities",
}

# Link badge tokens in project titles
LINK_BADGE_WORDS: Set[str] = {
    "live", "github", "demo", "code", "website", "site", "link",
    "preview", "app", "video", "paper", "view", "pdf", "repo", "source"
}

# Canonical skill taxonomy dictionary
SKILL_TAXONOMY: Dict[str, str] = {
    "python": "Programming Language",
    "javascript": "Programming Language",
    "typescript": "Programming Language",
    "java": "Programming Language",
    "c++": "Programming Language",
    "c#": "Programming Language",
    "c": "Programming Language",
    "go": "Programming Language",
    "golang": "Programming Language",
    "rust": "Programming Language",
    "ruby": "Programming Language",
    "php": "Programming Language",
    "scala": "Programming Language",
    "kotlin": "Programming Language",
    "swift": "Programming Language",
    "dart": "Programming Language",
    "sql": "Database",
    "html": "Frontend",
    "html5": "Frontend",
    "css": "Frontend",
    "css3": "Frontend",
    "sass": "Frontend",
    "react": "Frontend",
    "react.js": "Frontend",
    "reactjs": "Frontend",
    "react native": "Frontend",
    "next.js": "Frontend",
    "vue": "Frontend",
    "vue.js": "Frontend",
    "angular": "Frontend",
    "tailwind": "Frontend",
    "tailwind css": "Frontend",
    "bootstrap": "Frontend",
    "fastapi": "Backend",
    "flask": "Backend",
    "django": "Backend",
    "node.js": "Backend",
    "nodejs": "Backend",
    "express": "Backend",
    "express.js": "Backend",
    "spring": "Backend",
    "spring boot": "Backend",
    "postgresql": "Database",
    "postgres": "Database",
    "mysql": "Database",
    "mongodb": "Database",
    "redis": "Database",
    "sqlite": "Database",
    "oracle": "Database",
    "elasticsearch": "Database",
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "k8s": "DevOps",
    "aws": "DevOps",
    "amazon web services": "DevOps",
    "azure": "DevOps",
    "gcp": "DevOps",
    "google cloud": "DevOps",
    "git": "Tools & Platforms",
    "github": "Tools & Platforms",
    "gitlab": "Tools & Platforms",
    "linux": "Tools & Platforms",
    "postman": "Tools & Platforms",
    "jira": "Tools & Platforms",
    "power bi": "Tools & Platforms",
    "powerbi": "Tools & Platforms",
    "tableau": "Tools & Platforms",
    "excel": "Tools & Platforms",
    "pandas": "AI & Machine Learning",
    "numpy": "AI & Machine Learning",
    "scikit-learn": "AI & Machine Learning",
    "tensorflow": "AI & Machine Learning",
    "pytorch": "AI & Machine Learning",
    "keras": "AI & Machine Learning",
    "opencv": "AI & Machine Learning",
    "nlp": "AI & Machine Learning",
    "llm": "AI & Machine Learning",
    "machine learning": "AI & Machine Learning",
    "deep learning": "AI & Machine Learning",
}

CANONICAL_SKILL_CASING: Dict[str, str] = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "fastapi": "FastAPI",
    "react": "React",
    "react.js": "React.js",
    "react native": "React Native",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "html": "HTML5",
    "css": "CSS3",
    "sql": "SQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "linux": "Linux",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "tableau": "Tableau",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-learn",
    "go": "Go",
    "golang": "Go",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "c++": "C++",
    "tensorrt": "TensorRT",
    "opencv": "OpenCV",
    "sqlalchemy": "SQLAlchemy",
    "ollama": "Ollama",
    "windowfunctions": "Window Functions",
    "window functions": "Window Functions",
    "advanced sql": "Advanced SQL",
    "pivot tables": "Pivot Tables",
    "xlookup": "XLOOKUP",
    "convlstm": "ConvLSTM",
    "cnn": "CNN",
    "ai/machine learning": "AI/Machine Learning",
    "rest": "REST APIs",
    "rest apis": "REST APIs",
    "rest api": "REST APIs",
    "matlab": "MATLAB",
}

DATE_RANGE_REGEX = re.compile(
    r"\b(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s*)?(?:19|20)\d{2}\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*(?:(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s*)?(?:19|20)\d{2}|Present|Current|Ongoing)\b",
    re.IGNORECASE,
)
SINGLE_DATE_REGEX = re.compile(
    r"\b(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+)?(?:19|20)\d{2}\b",
    re.IGNORECASE,
)
BULLET_PREFIX_REGEX = re.compile(r"^[\s\-•*–—·▪●◦⋄\u2022\u00b7\u25aa\u25cf\u25e6\u2219\u25cb\uf0b7]+|^\s*\d+[\.\)]\s*")


class SkillList(list):
    """List subclass that supports both string containment checks (e.g. 'Python' in skills)
    and iterating/accessing rich skill dictionaries with 'name', 'category', 'source_evidence'.
    """
    def __contains__(self, item: Any) -> bool:
        if isinstance(item, str):
            item_lower = item.lower().strip()
            return any(
                (s if isinstance(s, str) else s.get("name", "")).lower().strip() == item_lower
                for s in self
            )
        return super().__contains__(item)


def normalize_unicode_text(text: str) -> str:
    """Normalizes Unicode characters, whitespace, and non-standard spacing while preserving quotes and dashes."""
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)
    t = t.replace("\u00a0", " ").replace("\u202f", " ")
    return t


def strip_bullet_prefix(text: str) -> str:
    """Removes bullet symbols or leading numbers from the beginning of a line."""
    if not text:
        return ""
    return BULLET_PREFIX_REGEX.sub("", text.strip()).strip()


def is_bullet_line(text: str) -> bool:
    """Detects if text begins with a bullet marker."""
    if not text:
        return False
    return bool(BULLET_PREFIX_REGEX.match(text.strip()))


class RecordGroupingService:
    """Assembles LayoutLMv3 predictions and PyMuPDF layout features into clean structured resume records."""

    SECTION_PATTERNS = {
        "summary": r"^(?:professional\s+|executive\s+)?(?:summary|profile|about\s+me|objective)\b",
        "skills": r"^(?:technical\s+|core\s+|key\s+)?(?:skills|competencies|technologies|tools|expertise|technical\s+exposure)\b",
        "experience": r"^(?:work\s+|professional\s+|relevant\s+|employment\s+|research\s+)?(?:experience|employment|work\s+history|history)\b",
        "projects": r"^(?:key\s+|personal\s+|academic\s+|technical\s+|featured\s+)?(?:projects|portfolio)\b",
        "education": r"^(?:education|academic\s+background|academic\s+credentials|qualifications|academic\s+history)\b",
        "certifications": r"^(?:certifications?|certificates?|licenses?|courses?)\b",
        "achievements": r"^(?:awards?|achievements?|honors?|key\s+achievements?)\b",
    }

    CUSTOM_SECTION_PATTERNS = [
        r"^(?:volunteering|community\s+service|community\s+outreach)\b",
        r"^(?:publications?|papers?)\b",
        r"^(?:patents?)\b",
        r"^(?:activities|extracurricular\s+activities)\b",
        r"^(?:languages|spoken\s+languages)\b",
        r"^(?:interests|hobbies)\b",
    ]

    def group_records(
        self,
        layout_lines: List[Dict[str, Any]],
        links: List[Dict[str, Any]],
        tokens: Optional[List[Dict[str, Any]]] = None,
        raw_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Groups extracted layout lines and model token classifications into final structured records."""
        sections_lines, custom_sections = self._segment_sections(layout_lines)

        personal_info = self._extract_personal_info(
            header_lines=sections_lines.get("header", []),
            all_lines=layout_lines,
            links=links,
        )

        summary = self._extract_summary(sections_lines.get("summary", []))
        education = self._extract_education(sections_lines.get("education", []))
        experience = self._extract_experience(sections_lines.get("experience", []))
        projects = self._extract_projects(sections_lines.get("projects", []), links=links)

        cert_lines = sections_lines.get("certifications", [])
        ach_lines = sections_lines.get("achievements", [])
        certifications = self._extract_certifications(cert_lines, ach_lines, links=links)

        skills = self._extract_skills(
            skills_lines=sections_lines.get("skills", []),
            projects=projects,
            all_lines=layout_lines,
        )

        formatted_custom = {}
        for sec_name, sec_items in custom_sections.items():
            content_str = "\n".join(l["text"] for l in sec_items if l.get("text")).strip()
            if content_str:
                formatted_custom[sec_name] = content_str

        return {
            "personal_info": personal_info,
            "summary": summary,
            "skills": skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications,
            "custom_sections": formatted_custom,
            "sections_found": list(sections_lines.keys()) + list(formatted_custom.keys()),
        }

    def _segment_sections(
        self, layout_lines: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
        """Segments lines into sections, separating standard sections and custom sections."""
        standard_sections: Dict[str, List[Dict[str, Any]]] = {
            "header": [],
            "summary": [],
            "skills": [],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
            "achievements": [],
        }
        custom_sections: Dict[str, List[Dict[str, Any]]] = {}

        curr_sec = "header"

        cand_name_lower = ""
        cand_pool = []
        for l in layout_lines:
            if l.get("page", 0) != 0 or l.get("bbox", [0, 0, 0, 0])[1] > 180:
                continue
            raw_text = normalize_unicode_text(l["text"]).strip()
            clean_name = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "", raw_text)
            clean_name = re.sub(r"(?:\+?\d{1,3}[\s-]?)?\(?\d{2,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5}", "", clean_name)
            clean_name = re.sub(r"https?://\S+", "", clean_name)
            clean_name = clean_name.replace("GitHub", "").replace("LinkedIn", "").strip(" –-|,/|")
            words = clean_name.split()
            if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                if not any(clean_name.lower() == h or clean_name.lower().startswith(h) for h in KNOWN_SECTION_HEADINGS):
                    cand_pool.append((clean_name, l.get("max_size", 10.0), l.get("is_bold", False)))

        if cand_pool:
            cand_pool.sort(key=lambda x: (x[1], x[2]), reverse=True)
            cand_name_lower = cand_pool[0][0].lower()

        for l in layout_lines:
            t = normalize_unicode_text(l["text"]).strip()
            if not t:
                continue

            if cand_name_lower and (t.lower() == cand_name_lower or cand_name_lower in t.lower()):
                standard_sections["header"].append(l)
                continue

            is_bullet = is_bullet_line(t)
            clean_t = strip_bullet_prefix(t).strip(": \t")
            words = clean_t.split()

            # Inline section heading check (e.g. 'SKILLS: Java, Spring Boot, MySQL...')
            if ":" in t and not is_bullet:
                prefix_candidate = t.split(":", 1)[0].strip()
                prefix_clean = strip_bullet_prefix(prefix_candidate).strip()
                if 1 <= len(prefix_clean.split()) <= 4:
                    matched_inline = None
                    for s_name, pat in self.SECTION_PATTERNS.items():
                        if re.search(pat, prefix_clean.lower()):
                            matched_inline = s_name
                            break
                    if matched_inline:
                        curr_sec = matched_inline
                        remainder_text = t.split(":", 1)[1].strip()
                        new_line = dict(l)
                        new_line["text"] = remainder_text
                        standard_sections[curr_sec].append(new_line)
                        continue

            matched_sec = None
            # Check for section heading
            is_heading_candidate = (
                not is_bullet
                and (1 <= len(words) <= 6)
                and not re.search(r"\d", clean_t)
                and not any(u in clean_t.lower() for u in ["@", "http", ".com"])
                and (
                    l.get("is_bold")
                    or l.get("is_prominent")
                    or (clean_t.isupper() and len(clean_t) > 3)
                    or clean_t.istitle()
                )
            )

            if is_heading_candidate:
                for s_name, pat in self.SECTION_PATTERNS.items():
                    if re.search(pat, clean_t.lower()):
                        matched_sec = s_name
                        break

                if not matched_sec:
                    for c_pat in self.CUSTOM_SECTION_PATTERNS:
                        if re.search(c_pat, clean_t.lower()):
                            matched_sec = f"custom:{clean_t.title()}"
                            break

            if matched_sec:
                curr_sec = matched_sec
                if curr_sec.startswith("custom:"):
                    c_name = curr_sec[7:]
                    if c_name not in custom_sections:
                        custom_sections[c_name] = []
            else:
                if curr_sec.startswith("custom:"):
                    c_name = curr_sec[7:]
                    custom_sections[c_name].append(l)
                else:
                    standard_sections[curr_sec].append(l)

        return standard_sections, custom_sections

    def _extract_personal_info(
        self,
        header_lines: List[Dict[str, Any]],
        all_lines: List[Dict[str, Any]],
        links: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Extracts candidate contact details, clean headline, and links."""
        search_lines = header_lines if header_lines else all_lines[:8]
        combined_text = "\n".join(l["text"] for l in search_lines)

        # 1. Name
        name = ""
        cand_pool = []
        for l in search_lines:
            if l.get("page", 0) != 0 or l.get("bbox", [0, 0, 0, 0])[1] > 180:
                continue
            raw_text = normalize_unicode_text(l["text"]).strip()
            clean_name = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "", raw_text)
            clean_name = re.sub(r"(?:\+?\d{1,3}[\s-]?)?\(?\d{2,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5}", "", clean_name)
            clean_name = re.sub(r"https?://\S+", "", clean_name)
            clean_name = clean_name.replace("GitHub", "").replace("LinkedIn", "").strip(" –-|,/|")
            words = clean_name.split()
            if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                if not any(clean_name.lower() == h or clean_name.lower().startswith(h) for h in KNOWN_SECTION_HEADINGS):
                    cand_pool.append((clean_name, l.get("max_size", 10.0), l.get("is_bold", False)))

        if cand_pool:
            cand_pool.sort(key=lambda x: (x[1], x[2]), reverse=True)
            name = cand_pool[0][0]
        elif search_lines:
            t0 = normalize_unicode_text(search_lines[0]["text"]).split("|")[0].strip()
            if not any(t0.lower() == h or t0.lower().startswith(h) for h in KNOWN_SECTION_HEADINGS):
                name = t0

        # 2. Email
        email = ""
        email_m = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", combined_text)
        if email_m:
            email = email_m.group(0).strip()
        else:
            for lk in links:
                if "mailto:" in lk.get("uri", ""):
                    email = lk["uri"].replace("mailto:", "").split("?")[0].strip()
                    break

        # 3. Phone
        phone = ""
        phone_m = re.search(r"(?:\+?\d{1,3}[\s-]?)?\(?\d{2,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5}", combined_text)
        if phone_m:
            phone = phone_m.group(0).strip()

        # 4. Location
        location = ""
        for line in search_lines:
            t = normalize_unicode_text(line["text"])
            loc_m = re.search(r"(?:Location\s*:\s*|in\s+)?([A-Za-z\s]+,\s*[A-Za-z\s]+)", t)
            if loc_m and "@" not in loc_m.group(1):
                clean_loc = re.sub(r"\b(?:github|linkedin|portfolio|email|phone|website)\b.*$", "", loc_m.group(1), flags=re.IGNORECASE).strip(" –-|,/|")
                if clean_loc:
                    location = clean_loc
                    break

        # 5. Professional Headline (Bug 1 fix: returns actual title, not 'title summary')
        headline = ""
        role_keywords = [
            "software engineer", "developer", "data scientist", "data analyst",
            "full-stack", "frontend", "backend", "machine learning engineer",
            "cloud architect", "devops engineer", "consultant", "intern"
        ]
        for line in search_lines:
            t = normalize_unicode_text(line["text"]).strip()
            if t == name:
                continue
            # Strip email, phone, and standard links to isolate headline text
            clean_hd = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "", t)
            clean_hd = re.sub(r"(?:\+?\d{1,3}[\s-]?)?\(?\d{2,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5}", "", clean_hd)
            clean_hd = re.sub(r"\b(?:linkedin|github|portfolio|email|phone|website)\b", "", clean_hd, flags=re.IGNORECASE).strip(" –-|,/|")
            hd_low = clean_hd.lower()
            if any(rk in hd_low for rk in role_keywords) and len(clean_hd.split()) <= 10:
                headline = clean_hd
                break

        # 6. Links (GitHub, LinkedIn, Portfolio)
        github_url, linkedin_url, portfolio_url = "", "", ""
        for lk in links:
            uri = lk.get("uri", "").strip()
            if "github.com" in uri.lower() and not github_url:
                github_url = uri
            elif "linkedin.com" in uri.lower() and not linkedin_url:
                linkedin_url = uri
            elif any(proto in uri.lower() for proto in ["http://", "https://"]) and not portfolio_url:
                if not any(domain in uri.lower() for domain in ["github.com", "linkedin.com"]):
                    portfolio_url = uri

        if not github_url:
            gh_m = re.search(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+", combined_text)
            if gh_m:
                github_url = gh_m.group(0)
                if not github_url.startswith("http"):
                    github_url = "https://" + github_url
        if not linkedin_url:
            li_m = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", combined_text)
            if li_m:
                linkedin_url = li_m.group(0)
                if not linkedin_url.startswith("http"):
                    linkedin_url = "https://" + linkedin_url

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "headline": headline,
            "github_url": github_url,
            "linkedin_url": linkedin_url,
            "portfolio_url": portfolio_url,
        }

    def _extract_summary(self, summary_lines: List[Dict[str, Any]]) -> str:
        """Extracts clean professional summary text."""
        bullets: List[str] = []
        for l in summary_lines:
            t = normalize_unicode_text(l["text"]).strip()
            if not t:
                continue
            clean_t = strip_bullet_prefix(t)
            if clean_t:
                bullets.append(clean_t)
        return " ".join(bullets).strip()

    def _extract_education(self, edu_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts structured education entries (institution, degree, dates, grade/CGPA)."""
        records: List[Dict[str, Any]] = []
        if not edu_lines:
            return records

        curr_rec: Optional[Dict[str, Any]] = None
        degree_keywords = [
            "bachelor", "master", "b.e", "b.tech", "m.tech", "m.s", "ph.d",
            "b.sc", "m.sc", "bca", "mca", "b.com", "diploma", "high school"
        ]

        for line in edu_lines:
            t = line["text"].strip()
            if not t:
                continue

            t_low = t.lower()
            is_degree_line = any(dk in t_low for dk in degree_keywords)

            if is_degree_line or curr_rec is None:
                if curr_rec and (curr_rec["degree"] or curr_rec["institution"]):
                    records.append(curr_rec)

                degree = ""
                inst = ""
                if " | " in t:
                    parts = t.split(" | ", 1)
                    degree = parts[0].strip()
                    inst = parts[1].strip()
                elif "," in t and is_degree_line:
                    parts = t.split(",", 1)
                    degree = parts[0].strip()
                    inst = parts[1].strip()
                else:
                    degree = t

                curr_rec = {
                    "degree": degree,
                    "institution": inst,
                    "field_of_study": "",
                    "start_date": "",
                    "end_date": "",
                    "grade": "",
                    "grade_type": "",
                }
                continue

            # Check for pure date line
            clean_no_dates = DATE_RANGE_REGEX.sub("", t).strip(" –-|,()[]")
            clean_single = SINGLE_DATE_REGEX.sub("", t).strip(" –-|,()[]")
            if (DATE_RANGE_REGEX.search(t) and not clean_no_dates) or (SINGLE_DATE_REGEX.search(t) and not clean_single):
                d_raw = (DATE_RANGE_REGEX.search(t) or SINGLE_DATE_REGEX.search(t)).group(0).strip()
                parts = re.split(r"\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*", d_raw, flags=re.IGNORECASE)
                curr_rec["start_date"] = parts[0].strip() if len(parts) > 1 else ""
                curr_rec["end_date"] = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                continue

            # Check for dates within line
            date_m = DATE_RANGE_REGEX.search(t) or SINGLE_DATE_REGEX.search(t)
            if date_m:
                d_raw = date_m.group(0).strip()
                parts = re.split(r"\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*", d_raw, flags=re.IGNORECASE)
                curr_rec["start_date"] = parts[0].strip() if len(parts) > 1 else ""
                curr_rec["end_date"] = parts[1].strip() if len(parts) > 1 else parts[0].strip()

            # Check for grade or CGPA
            grade_m = re.search(r"(?:CGPA|GPA|Percentage|Score|Grade)\s*[:=]?\s*(\d+(?:\.\d+)?(?:\s*/\s*\d+)?%?)", t, re.IGNORECASE)
            if grade_m:
                curr_rec["grade"] = grade_m.group(1).strip()
                curr_rec["grade_type"] = "CGPA" if "cgpa" in t_low else ("GPA" if "gpa" in t_low else "Percentage")
            elif not curr_rec["institution"] and not is_bullet_line(t) and len(t.split()) <= 8:
                curr_rec["institution"] = t

        if curr_rec and (curr_rec["degree"] or curr_rec["institution"]):
            records.append(curr_rec)

        return records

    def _extract_experience(self, exp_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts work experience records, resolving multi-role and wrapped bullet points."""
        records: List[Dict[str, Any]] = []
        if not exp_lines:
            return records

        curr_rec: Optional[Dict[str, Any]] = None
        last_company = ""

        role_words = [
            "engineer", "developer", "lead", "architect", "intern", "manager",
            "analyst", "consultant", "specialist", "officer", "designer", "scientist", "fellow", "researcher"
        ]

        for line in exp_lines:
            t = normalize_unicode_text(line["text"]).strip()
            if not t:
                continue

            is_bullet = is_bullet_line(t)
            clean_t = strip_bullet_prefix(t)
            first_w = clean_t.split()[0].lower() if clean_t.split() else ""

            # 1. Pure date line (e.g. 'Jan 2026 – Mar 2026')
            clean_no_dates = DATE_RANGE_REGEX.sub("", t).strip(" –-|,()[]")
            clean_single = SINGLE_DATE_REGEX.sub("", t).strip(" –-|,()[]")
            if (DATE_RANGE_REGEX.search(t) and not clean_no_dates) or (SINGLE_DATE_REGEX.search(t) and not clean_single):
                if curr_rec:
                    d_raw = (DATE_RANGE_REGEX.search(t) or SINGLE_DATE_REGEX.search(t)).group(0).strip()
                    parts = re.split(r"\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*", d_raw, flags=re.IGNORECASE)
                    curr_rec["start_date"] = parts[0].strip() if len(parts) > 1 else ""
                    curr_rec["end_date"] = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                    curr_rec["is_current"] = any(c in curr_rec["end_date"].lower() for c in ["present", "current", "ongoing"])
                continue

            # 2. Company / location line right after role initialization
            if curr_rec and not curr_rec["bullets"] and not is_bullet and first_w not in ACTION_VERBS:
                if curr_rec["company"] in ("Organization", ""):
                    if "(" in t and ")" in t and len(t.split()) <= 8:
                        comp_part = re.sub(r"\(.*?\)", "", t).strip(" –-|,")
                        loc_part = re.search(r"\((.*?)\)", t).group(1).strip()
                        curr_rec["company"] = comp_part
                        curr_rec["location"] = loc_part
                        last_company = curr_rec["company"]
                        continue
                    elif " | " in t:
                        c_part, l_part = t.split(" | ", 1)
                        curr_rec["company"] = c_part.strip()
                        curr_rec["location"] = l_part.strip()
                        last_company = curr_rec["company"]
                        continue
                    elif " - " in t and not is_bullet:
                        c_part, l_part = t.split(" - ", 1)
                        curr_rec["company"] = c_part.strip()
                        curr_rec["location"] = l_part.strip()
                        last_company = curr_rec["company"]
                        continue
                    elif len(t.split()) <= 6 and not DATE_RANGE_REGEX.search(t):
                        curr_rec["company"] = t
                        last_company = curr_rec["company"]
                        continue

            # 3. Check if this line is an experience role header
            is_role_header = (
                not is_bullet
                and first_w not in ACTION_VERBS
                and (
                    any(rw in t.lower() for rw in role_words)
                    or " | " in t
                    or " at " in t
                    or (line.get("is_bold") and len(t.split()) <= 10)
                    or (curr_rec is None and len(t.split()) <= 10)
                )
            )

            if is_role_header:
                if curr_rec and curr_rec["title"]:
                    records.append(curr_rec)

                title = ""
                company = ""
                location = ""
                start_date = ""
                end_date = ""
                is_current = False

                date_m = DATE_RANGE_REGEX.search(t)
                if date_m:
                    d_raw = date_m.group(0).strip()
                    parts = re.split(r"\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*", d_raw, flags=re.IGNORECASE)
                    start_date = parts[0].strip() if len(parts) > 1 else ""
                    end_date = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                    is_current = any(c in end_date.lower() for c in ["present", "current", "ongoing"])
                    t = DATE_RANGE_REGEX.sub("", t).strip(" –-|,")

                if " | " in t:
                    parts = t.split(" | ")
                    title = parts[0].strip()
                    if len(parts) >= 3:
                        company = parts[1].strip()
                        location = parts[2].strip()
                    elif len(parts) == 2:
                        company = parts[1].strip()
                elif " - " in t and not is_bullet:
                    parts = t.split(" - ", 1)
                    title = parts[0].strip()
                    company = parts[1].strip()
                elif " at " in t:
                    parts = t.split(" at ", 1)
                    title = parts[0].strip()
                    company = parts[1].strip()
                else:
                    title = t

                if "(" in company and ")" in company:
                    c_clean = re.sub(r"\(.*?\)", "", company).strip(" –-|,")
                    l_clean = re.search(r"\((.*?)\)", company).group(1).strip()
                    company = c_clean
                    if not location:
                        location = l_clean

                if not company and last_company:
                    company = last_company
                elif company:
                    last_company = company

                curr_rec = {
                    "title": title,
                    "company": company or "Organization",
                    "location": location,
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_current": is_current,
                    "bullets": [],
                }
                continue

            if curr_rec and not curr_rec["bullets"]:
                loc_date_m = DATE_RANGE_REGEX.search(t)
                if loc_date_m and not curr_rec["end_date"]:
                    d_raw = loc_date_m.group(0).strip()
                    parts = re.split(r"\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*", d_raw, flags=re.IGNORECASE)
                    curr_rec["start_date"] = parts[0].strip() if len(parts) > 1 else ""
                    curr_rec["end_date"] = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                    curr_rec["is_current"] = any(c in curr_rec["end_date"].lower() for c in ["present", "current", "ongoing"])
                    continue

                if ("(" in t and ")" in t) or ("," in t and len(t.split()) <= 4):
                    curr_rec["location"] = t.strip("()")
                    continue

            if curr_rec:
                if is_bullet:
                    curr_rec["bullets"].append(clean_t)
                elif curr_rec["bullets"] and not line.get("is_bold"):
                    curr_rec["bullets"][-1] += f" {clean_t}"
                elif first_w in ACTION_VERBS:
                    curr_rec["bullets"].append(clean_t)

        if curr_rec and curr_rec["title"]:
            records.append(curr_rec)

        return records

    def _extract_projects(
        self, proj_lines: List[Dict[str, Any]], links: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extracts structured project records, technologies, dates, and isolated links."""
        records: List[Dict[str, Any]] = []
        if not proj_lines:
            return records

        curr_proj: Optional[Dict[str, Any]] = None

        SUB_BULLET_LABELS = {
            "key achievement", "key achievements", "achievement", "achievements",
            "feature", "features", "highlight", "highlights", "responsibility",
            "responsibilities", "impact", "result", "results", "note", "notes",
            "overview", "details"
        }

        def is_tech_line(s: str) -> bool:
            s_low = s.lower().strip()
            if any(s_low.startswith(p) for p in [
                "technologies:", "tech stack:", "tools:", "built with:", "stack:",
                "technologies used:", "key technologies:", "tools used:", "environment:"
            ]):
                return True
            if s.startswith("(") and s.endswith(")"):
                inner = s[1:-1].strip()
                if any(k in inner.lower() for k in ["python", "sql", "react", "java", "node", "aws"]) or "," in inner:
                    return True
            # Disqualify full sentences ending in punctuation from being treated as bare tech lists
            if s.rstrip().endswith((".", ";")):
                return False
            if "," in s and not is_bullet_line(s):
                parts = [p.strip() for p in s.split(",") if p.strip()]
                if 2 <= len(parts) <= 15 and all(len(p.split()) <= 4 for p in parts):
                    has_sentence_clause = any(
                        p.lower().startswith(("and ", "with ", "for ", "the ", "or ", "in ", "by ", "reducing ", "improving ", "ensuring ", "using "))
                        for p in parts
                    )
                    if not has_sentence_clause:
                        first_w = parts[0].split()[0].lower() if parts[0].split() else ""
                        if first_w not in ACTION_VERBS:
                            return True
            return False

        def clean_title_and_badges(raw_title: str) -> Tuple[str, List[str]]:
            clean_t = raw_title
            techs: List[str] = []
            for b in re.findall(r"\[(.*?)\]", clean_t):
                if b.strip().lower() in LINK_BADGE_WORDS:
                    clean_t = clean_t.replace(f"[{b}]", "").strip()
                elif "," in b or any(k in b.lower() for k in ["python", "react", "java", "node", "sql", "aws", "docker"]):
                    techs.extend([x.strip() for x in b.split(",") if x.strip()])
                    clean_t = clean_t.replace(f"[{b}]", "").strip()
            for p in re.findall(r"\((.*?)\)", clean_t):
                if p.strip().lower() in LINK_BADGE_WORDS:
                    clean_t = clean_t.replace(f"({p})", "").strip()
                elif "," in p or any(k in p.lower() for k in ["python", "react", "java", "node", "sql", "aws", "docker"]):
                    techs.extend([x.strip() for x in p.split(",") if x.strip()])
                    clean_t = clean_t.replace(f"({p})", "").strip()
            return clean_t.strip(" –-|,"), techs

        def is_pure_date(s: str) -> bool:
            clean_s = DATE_RANGE_REGEX.sub("", s).strip(" –-|,()[]")
            if not clean_s and (DATE_RANGE_REGEX.search(s) or SINGLE_DATE_REGEX.search(s)):
                return True
            clean_single = SINGLE_DATE_REGEX.sub("", s).strip(" –-|,()[]")
            if not clean_single and SINGLE_DATE_REGEX.search(s):
                return True
            return False

        used_links: Set[str] = set()
        pending_bullet: bool = False

        for line in proj_lines:
            t = line["text"].strip()
            if not t:
                continue

            is_bullet = is_bullet_line(t)
            clean_t = strip_bullet_prefix(t)

            # Standalone bullet glyph indicator without text
            if not clean_t:
                if is_bullet:
                    pending_bullet = True
                continue

            if pending_bullet:
                is_bullet = True
                pending_bullet = False

            first_w = clean_t.split()[0].lower() if clean_t.split() else ""
            is_tech = is_tech_line(t)

            # 1. Pure date line (e.g. '2023 to Present')
            if is_pure_date(t):
                if curr_proj:
                    dt_m = DATE_RANGE_REGEX.search(t) or SINGLE_DATE_REGEX.search(t)
                    if dt_m:
                        d_raw = dt_m.group(0).strip()
                        parts = re.split(r"\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*", d_raw, flags=re.IGNORECASE)
                        curr_proj["start_date"] = parts[0].strip() if len(parts) > 1 else ""
                        curr_proj["end_date"] = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                continue

            # 2. Tech stack line
            if curr_proj and is_tech:
                clean_tech = re.sub(
                    r"^(?:technologies(?: used)?|tech stack|tools(?: used)?|built with|stack|environment|key technologies):\s*",
                    "",
                    t,
                    flags=re.IGNORECASE,
                )
                clean_tech = clean_tech.replace("[Live]", "").replace("[Code]", "").replace("[Demo]", "")
                clean_tech = clean_tech.replace("(Live)", "").replace("(Demo)", "")
                parts = [p.strip() for p in clean_tech.strip("()").split(",") if p.strip()]
                for pt in parts:
                    if pt.lower() not in LINK_BADGE_WORDS and pt not in curr_proj["technologies"]:
                        curr_proj["technologies"].append(pt)
                continue

            # 3. Inline title-description format: "Title: Description"
            # e.g. "System Automation & Monitoring Scripts: Developed Python and shell scripts..."
            has_inline_desc = False
            inline_title = ""
            inline_desc = ""
            if ":" in clean_t and not is_tech:
                cand_pfx, cand_rest = clean_t.split(":", 1)
                cand_pfx = cand_pfx.strip()
                cand_rest = cand_rest.strip()
                cand_pfx_words = cand_pfx.split()
                cand_rest_words = cand_rest.split()
                cand_pfx_first = cand_pfx_words[0].lower() if cand_pfx_words else ""
                cand_rest_first = cand_rest_words[0].lower() if cand_rest_words else ""

                if (
                    1 <= len(cand_pfx_words) <= 12
                    and cand_rest
                    and cand_pfx_first not in ACTION_VERBS
                    and cand_pfx.lower() not in SUB_BULLET_LABELS
                    and not any(cand_pfx.lower().startswith(p) for p in [
                        "technologies", "tech stack", "tools", "built with", "stack", "environment", "key technologies"
                    ])
                    and (
                        cand_rest_first in ACTION_VERBS
                        or line.get("is_bold")
                        or is_bullet
                        or curr_proj is None
                        or len(cand_pfx_words) <= 8
                    )
                ):
                    has_inline_desc = True
                    inline_title = cand_pfx
                    inline_desc = cand_rest

            # 4. Title detection
            has_explicit_boundary = (
                line.get("is_bold")
                or bool(DATE_RANGE_REGEX.search(t))
                or bool(SINGLE_DATE_REGEX.search(t))
                or any(sep in t for sep in ["|", "—", "–", " - ", "[", "("])
            )

            is_title = has_inline_desc or (
                not is_bullet
                and not is_tech
                and not t.endswith(".")
                and not t.startswith("http")
                and first_w not in ACTION_VERBS
                and len(t.split()) <= 20
                and bool(t and (t[0].isupper() or t[0].isdigit()))
                and (
                    curr_proj is None
                    or (has_explicit_boundary and (curr_proj["bullets"] or len(t.split()) <= 15))
                )
            )

            if is_title:
                if curr_proj and curr_proj["title"]:
                    records.append(curr_proj)

                raw_title = inline_title if has_inline_desc else t
                clean_title, inline_techs = clean_title_and_badges(raw_title)
                start_date, end_date = "", ""

                date_m = DATE_RANGE_REGEX.search(clean_title) or SINGLE_DATE_REGEX.search(clean_title)
                if date_m:
                    d_raw = date_m.group(0).strip()
                    parts = re.split(r"\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*", d_raw, flags=re.IGNORECASE)
                    start_date = parts[0].strip() if len(parts) > 1 else ""
                    end_date = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                    clean_title = DATE_RANGE_REGEX.sub("", clean_title).strip(" –-|,")
                    clean_title = SINGLE_DATE_REGEX.sub("", clean_title).strip(" –-|,")

                if " | " in clean_title:
                    p_parts = clean_title.split(" | ", 1)
                    clean_title = p_parts[0].strip()
                    inline_techs.extend([x.strip() for x in p_parts[1].split(",") if x.strip()])

                # Match links for this project
                github_url, live_url = "", ""
                line_bbox = line.get("bbox", [0, 0, 0, 0])
                title_words = [w.lower() for w in re.findall(r"[a-zA-Z0-9]+", clean_title) if len(w) > 2]

                for lk in links:
                    uri = lk.get("uri", "")
                    if uri in used_links:
                        continue
                    r = lk.get("rect")
                    is_match = False
                    if r and len(r) == 4:
                        if abs(r[1] - line_bbox[1]) < 60 or abs(r[3] - line_bbox[3]) < 60:
                            is_match = True
                    # Keyword matching on URI
                    if not is_match and any(w in uri.lower() for w in title_words):
                        is_match = True

                    if is_match:
                        if "github.com" in uri.lower() and not github_url:
                            github_url = uri
                            used_links.add(uri)
                        elif not live_url and not ("github.com" in uri.lower() and github_url):
                            live_url = uri
                            used_links.add(uri)

                curr_proj = {
                    "title": clean_title.strip(" –-|,"),
                    "description": inline_desc if has_inline_desc else "",
                    "start_date": start_date,
                    "end_date": end_date,
                    "technologies": inline_techs,
                    "url": live_url or github_url,
                    "github_url": github_url,
                    "live_url": live_url,
                    "bullets": [inline_desc] if (has_inline_desc and inline_desc) else [],
                }
                continue

            if curr_proj and not curr_proj["end_date"]:
                dt_m = DATE_RANGE_REGEX.search(t)
                if dt_m:
                    d_raw = dt_m.group(0).strip()
                    parts = re.split(r"\s*(?:[\-–—/·\u00b7]+|\bto\b)\s*", d_raw, flags=re.IGNORECASE)
                    curr_proj["start_date"] = parts[0].strip() if len(parts) > 1 else ""
                    curr_proj["end_date"] = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                    continue

            if curr_proj:
                if is_bullet:
                    curr_proj["bullets"].append(clean_t)
                elif curr_proj["bullets"]:
                    curr_proj["bullets"][-1] += f" {clean_t}"
                    if len(curr_proj["bullets"]) == 1:
                        curr_proj["description"] = curr_proj["bullets"][0]
                elif first_w in ACTION_VERBS:
                    curr_proj["bullets"].append(clean_t)
                elif not curr_proj["description"] and len(t.split()) > 4:
                    curr_proj["description"] = clean_t
                else:
                    curr_proj["bullets"].append(clean_t)
            elif clean_t:
                # Preserve unclassified text before any project title
                curr_proj = {
                    "title": clean_t,
                    "description": "",
                    "start_date": "",
                    "end_date": "",
                    "technologies": [],
                    "url": "",
                    "github_url": "",
                    "live_url": "",
                    "bullets": [],
                }

        if curr_proj and curr_proj["title"]:
            records.append(curr_proj)

        cleaned_records = []
        for r in records:
            r["bullets"] = [b.strip() for b in r.get("bullets", []) if b and b.strip()]
            cleaned_records.append(r)

        return cleaned_records

    def _extract_certifications(
        self,
        cert_lines: List[Dict[str, Any]],
        ach_lines: List[Dict[str, Any]],
        links: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extracts certifications and achievements, preserving credential links and issuers."""
        records: List[Dict[str, Any]] = []
        combined_lines = cert_lines + ach_lines

        curr_cert: Optional[Dict[str, Any]] = None

        for line in combined_lines:
            t = normalize_unicode_text(line["text"]).strip()
            if not t:
                continue

            clean_t = strip_bullet_prefix(t)
            if not clean_t:
                continue

            # Check if this line is Credential ID for current cert
            id_m = re.search(r"(?:Credential\s+ID|License\s+ID|ID)\s*[:=]\s*([A-Za-z0-9\-]+)", clean_t, re.IGNORECASE)
            if id_m and curr_cert:
                curr_cert["credential_id"] = id_m.group(1).strip()
                continue

            if curr_cert:
                records.append(curr_cert)

            # Strip link badges
            clean_t = re.sub(r"\[(?:link|credential|verify|view|certificate)\]", "", clean_t, flags=re.IGNORECASE).strip(" –-|,")

            name = ""
            issuer = ""
            date_str = ""
            cred_id = ""
            cred_url = ""

            date_m = DATE_RANGE_REGEX.search(clean_t)
            if date_m:
                date_str = date_m.group(0).strip()
                clean_t = DATE_RANGE_REGEX.sub("", clean_t).strip(" –-|,")
            else:
                trail_date_m = re.search(r"(?:[\(|\[|\-|\||,]\s*)?\b(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+)?(?:19|20)\d{2}\s*(?:\)|\])?$", clean_t, re.IGNORECASE)
                if trail_date_m:
                    date_str = re.search(r"(?:19|20)\d{2}", trail_date_m.group(0)).group(0)
                    clean_t = clean_t[:trail_date_m.start()].strip(" –-|,([")

            if " - " in clean_t:
                parts = clean_t.split(" - ", 1)
                name = parts[0].strip()
                issuer = parts[1].strip()
            elif " | " in clean_t:
                parts = clean_t.split(" | ", 1)
                name = parts[0].strip()
                issuer = parts[1].strip()
            elif " by " in clean_t.lower():
                parts = re.split(r"\s+by\s+", clean_t, flags=re.IGNORECASE)
                name = parts[0].strip()
                issuer = parts[1].strip()
            else:
                name = clean_t

            line_bbox = line.get("bbox", [0, 0, 0, 0])
            for lk in links:
                uri = lk.get("uri", "")
                r = lk.get("rect")
                if r and len(r) == 4:
                    if abs(r[1] - line_bbox[1]) < 30:
                        cred_url = uri
                        break
                elif "verify" in uri.lower() or "cred" in uri.lower():
                    cred_url = uri
                    break

            curr_cert = {
                "name": name,
                "issuer": issuer,
                "issue_date": date_str,
                "expiry_date": "",
                "credential_id": cred_id,
                "credential_url": cred_url,
            }

        if curr_cert:
            records.append(curr_cert)

        return records

    def _extract_skills(
        self,
        skills_lines: List[Dict[str, Any]],
        projects: List[Dict[str, Any]],
        all_lines: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extracts candidate skills, categorizes into canonical taxonomy, and attaches source evidence."""
        skill_dict: Dict[str, Dict[str, Any]] = {}

        # 1. Merge wrapped continuation lines in skills section
        merged_lines: List[str] = []
        for line in skills_lines:
            t = normalize_unicode_text(line["text"]).strip()
            if not t:
                continue
            clean_t = strip_bullet_prefix(t)
            if not clean_t:
                continue
            if ":" in clean_t or not merged_lines:
                merged_lines.append(clean_t)
            else:
                prev = merged_lines[-1]
                if prev.endswith("REST") and clean_t.startswith("APIs"):
                    merged_lines[-1] = f"{prev} {clean_t}"
                elif prev.endswith(",") or clean_t.startswith(",") or prev.endswith("-") or prev.endswith("/"):
                    merged_lines[-1] = f"{prev} {clean_t}"
                else:
                    merged_lines[-1] = f"{prev}, {clean_t}"

        # 2. Tokenize each merged category line
        for line_text in merged_lines:
            category_hint = "Other"
            content = line_text

            if ":" in line_text:
                prefix, remainder = line_text.split(":", 1)
                p_low = prefix.lower().strip()
                if "language" in p_low:
                    category_hint = "Programming Language"
                elif "frontend" in p_low or "web" in p_low:
                    category_hint = "Frontend"
                elif "backend" in p_low:
                    category_hint = "Backend"
                elif "database" in p_low:
                    category_hint = "Database"
                elif "devops" in p_low or "cloud" in p_low:
                    category_hint = "DevOps"
                elif "tool" in p_low or "platform" in p_low:
                    category_hint = "Tools & Platforms"
                elif "soft" in p_low:
                    category_hint = "Soft Skills"
                elif "analytics" in p_low or "intelligence" in p_low:
                    category_hint = "Data & Analytics"
                content = remainder

            extracted_tokens: List[str] = []

            def replace_paren(m):
                inner = m.group(1).strip()
                # Acronym like (EDA) attached to preceding phrase
                if inner.isupper() and len(inner) <= 5 and "," not in inner and ";" not in inner:
                    return f"({inner})"
                # Proficiency descriptor like (Basics)
                if inner.lower() in {"basics", "intermediate", "advanced", "proficient", "basic", "hands-on"}:
                    return ""
                # Multi-skill group like (Pandas, NumPy)
                for item in re.split(r"[,;]+", inner):
                    clean_item = item.strip()
                    if clean_item and clean_item.lower() not in {"basics", "intermediate", "advanced", "proficient", "basic", "hands-on"}:
                        extracted_tokens.append(clean_item)
                return ""

            remainder_no_parens = re.sub(r"\((.*?)\)", replace_paren, content)
            for top_item in re.split(r"[,;]+", remainder_no_parens):
                clean_top = top_item.strip()
                if clean_top:
                    extracted_tokens.append(clean_top)

            for token in extracted_tokens:
                s_clean = re.sub(r"\s+", " ", token).strip("•*·▪–⋄◦ \t")
                if s_clean.startswith("(") and s_clean.endswith(")"):
                    s_clean = s_clean[1:-1].strip()
                if not s_clean or len(s_clean) > 40:
                    continue
                s_low = s_clean.lower()
                norm_key = re.sub(r"[^a-z0-9]", "", s_low)
                if norm_key in {"windowfunctions", "windowfunction"}:
                    cased_name = "Window Functions"
                    s_low = "window functions"
                elif s_low in {"rest", "rest apis", "rest api"}:
                    cased_name = "REST APIs"
                    s_low = "rest apis"
                else:
                    cased_name = CANONICAL_SKILL_CASING.get(s_low, s_clean)

                cat = SKILL_TAXONOMY.get(s_low, category_hint)
                if s_low not in skill_dict:
                    skill_dict[s_low] = {
                        "name": cased_name,
                        "category": cat,
                        "source_evidence": line_text,
                    }

        for p in projects:
            for tech in p.get("technologies", []):
                t_clean = normalize_unicode_text(tech).strip()
                if not t_clean:
                    continue
                t_low = t_clean.lower()
                cased = CANONICAL_SKILL_CASING.get(t_low, t_clean)
                cat = SKILL_TAXONOMY.get(t_low, "Other")
                if t_low not in skill_dict:
                    skill_dict[t_low] = {
                        "name": cased,
                        "category": cat,
                        "source_evidence": f"Project: {p.get('title', '')}",
                    }

        return list(skill_dict.values())


record_grouping_service = RecordGroupingService()
