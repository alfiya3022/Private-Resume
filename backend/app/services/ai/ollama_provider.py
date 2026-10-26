import json
import re
import time
from typing import Dict, List, Optional, Any, Tuple
import httpx
from app.core.config import settings
from app.schemas.analysis import StructuredJDAnalysis

# Categorized taxonomy for deterministic extraction and validation
TECH_CATEGORIES = {
    "languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php", "sql", "html", "css",
        "t-sql", "tsql", "transact-sql", "pl/sql", "plsql", "bash", "powershell", "shell", "r", "scala", "c"
    ],
    "frameworks": [
        "fastapi", "django", "flask", "react", "next.js", "vue", "angular", "express", "spring boot", "tailwind",
        ".net", "asp.net", "node.js", "nodejs"
    ],
    "databases": [
        "sql server", "ms sql server", "microsoft sql server", "postgresql", "postgres", "mysql", "mongodb", "redis",
        "elasticsearch", "sqlite", "dynamodb", "oracle", "oracle database", "mariadb", "cassandra", "snowflake",
        "bigquery", "redshift", "couchdb", "neo4j", "nosql", "rdbms", "relational database"
    ],
    "concepts": [
        "stored procedures", "stored procedure", "database administration", "dba", "sql backups", "backup and recovery",
        "data definition", "data manipulation", "data control", "transactional control", "ddl", "dml", "dcl", "tcl",
        "complex queries", "data queries", "query optimization", "indexing", "triggers", "database views",
        "etl", "data pipeline", "data warehousing", "data modeling", "database normalization", "database design",
        "database security", "replication", "sharding", "acid"
    ],
    "tools": [
        "excel", "microsoft excel", "microsoft office", "ms office", "outlook", "microsoft outlook",
        "power bi", "tableau", "ssis", "ssrs", "ssas", "ftp", "sftp", "secure ftp", "pgp", "encryption",
        "docker", "git", "github", "gitlab", "jira", "postman", "linux", "jenkins", "kubernetes", "latex",
        "rest api", "rest apis", "restful", "soap", "ci/cd"
    ],
    "cloud": [
        "aws", "azure", "gcp", "google cloud", "terraform", "s3", "lambda", "ec2"
    ],
    "soft_skills": [
        "communication", "teamwork", "leadership", "problem solving", "collaboration", "analytical", "mentoring",
        "customer-facing", "client management", "agile", "scrum"
    ],
}

CANONICAL_NAMES = {
    "sql server": "SQL Server", "ms sql server": "Microsoft SQL Server", "microsoft sql server": "Microsoft SQL Server",
    "stored procedures": "Stored Procedures", "stored procedure": "Stored Procedures",
    "database administration": "Database Administration", "dba": "Database Administration",
    "sql backups": "SQL Backups & Recovery", "backup and recovery": "Backup and Recovery",
    "data definition": "Data Definition (DDL)", "data manipulation": "Data Manipulation (DML)",
    "data control": "Data Control (DCL)", "transactional control": "Transactional Control (TCL)",
    "ddl": "DDL", "dml": "DML", "dcl": "DCL", "tcl": "TCL",
    "complex queries": "Complex SQL Queries", "data queries": "SQL Queries",
    "query optimization": "Query Optimization", "indexing": "Database Indexing",
    "triggers": "Database Triggers", "database views": "Database Views",
    "microsoft office": "Microsoft Office", "ms office": "Microsoft Office",
    "excel": "Microsoft Excel", "microsoft excel": "Microsoft Excel",
    "outlook": "Microsoft Outlook", "microsoft outlook": "Microsoft Outlook",
    "ftp": "FTP / SFTP", "sftp": "FTP / SFTP", "secure ftp": "Secure FTP", "pgp": "PGP Encryption",
    "encryption": "Data Encryption", "power bi": "Power BI", "tableau": "Tableau",
    "ssis": "SSIS", "ssrs": "SSRS", "ssas": "SSAS", "etl": "ETL",
    "data pipeline": "Data Pipelines", "data warehousing": "Data Warehousing",
    "t-sql": "T-SQL", "tsql": "T-SQL", "transact-sql": "Transact-SQL",
    "pl/sql": "PL/SQL", "plsql": "PL/SQL", "sql": "SQL",
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL", "oracle": "Oracle",
    "oracle database": "Oracle Database", "sqlite": "SQLite", "mongodb": "MongoDB", "redis": "Redis",
    "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript", "java": "Java",
    "c++": "C++", "c#": "C#", "go": "Go", "rust": "Rust", "html": "HTML", "css": "CSS",
    "docker": "Docker", "git": "Git", "github": "GitHub", "gitlab": "GitLab",
    "aws": "AWS", "azure": "Azure", "gcp": "GCP", "linux": "Linux", "kubernetes": "Kubernetes",
    "fastapi": "FastAPI", "django": "Django", "flask": "Flask", "react": "React", "next.js": "Next.js",
    "express": "Express", "tailwind": "Tailwind CSS", "spring boot": "Spring Boot",
    "rest api": "REST APIs", "rest apis": "REST APIs", "restful": "REST APIs", "ci/cd": "CI/CD",
    "postman": "Postman", "latex": "LaTeX", "jenkins": "Jenkins", "jira": "Jira",
    "customer-facing": "Customer-Facing Experience", "communication": "Communication",
    "analytical": "Analytical Thinking", "problem solving": "Problem Solving", "teamwork": "Team Collaboration",
    "agile": "Agile", "scrum": "Scrum",
}


def parse_jd_experience(text: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """Deterministic parser for JD experience requirements.

    Understands:
    - Ranges: '0-2 years', '0 to 2 years', '0–2 yrs', '1-3 years'
    - Plus / Minimum: '2+ years', 'at least 3 years', 'minimum 5 years'
    - Open-ended / Entry level: 'fresher', 'entry level' (min 0)

    Returns:
        (min_years, max_years, experience_range)
    """
    if not text:
        return None, None, "Not specified"

    # 1. Range patterns: 0-2 years, 0 to 2 years, 0–2 yrs, 1-3 years, min 1 to 2 years
    range_match = re.search(
        r"(?:minimum|at\s+least|min\.?)?\s*(\b\d+)\s*(?:-|–|—|\bto\b)\s*(\d+)\+?\s*(?:years?|yrs?)\b",
        text,
        re.IGNORECASE,
    )
    if range_match:
        min_y = int(range_match.group(1))
        max_y = int(range_match.group(2))
        return min_y, max_y, f"{min_y}-{max_y} years"

    # 2. Plus or minimum patterns: 2+ years, at least 3 years, minimum 5 years, 5+ yrs
    min_match = re.search(
        r"(?:(?:minimum|at\s+least|min\.?)\s+(\d+)\+?\s*(?:years?|yrs?)|(\d+)\+\s*(?:years?|yrs?))",
        text,
        re.IGNORECASE,
    )
    if min_match:
        val = int(min_match.group(1) or min_match.group(2))
        return val, None, f"{val}+ Years"

    # 3. Simple single year with year/yrs keyword: e.g. '3 years of experience'
    single_match = re.search(
        r"(\b\d+)\s*(?:years?|yrs?)(?:\s+of\s+(?:relevant\s+)?experience)?\b",
        text,
        re.IGNORECASE,
    )
    if single_match:
        val = int(single_match.group(1))
        return val, None, f"{val}+ Years"

    # 4. Fresher / entry level
    if re.search(r"\b(fresher|entry[\s\-]level)\b", text, re.IGNORECASE):
        return 0, None, "0+ years"

    return None, None, "Not specified"


class OllamaProvider:
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model

    async def is_available(self) -> bool:
        """Checks if local host Ollama service is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/version")
                return res.status_code == 200
        except Exception:
            return False

    async def analyze_job_description(self, raw_jd_text: str) -> StructuredJDAnalysis:
        """Analyzes raw job description text via Ollama or deterministic fallback."""
        prompt = (
            "You are an expert technical recruiter analyzing a job description. "
            "Extract structured technical requirements from the JD text below. "
            "Do NOT invent or hallucinate unmentioned skills. "
            "CRITICAL: Extract 'min_years' and 'max_years' ONLY if explicitly stated in the JD text. "
            "If the JD specifies a range such as '0 to 2 years' or '1-3 years', set min_years to the minimum (e.g. 0 or 1) and max_years to the maximum (e.g. 2 or 3). "
            "If it specifies '2+ years' or 'at least 3 years', set min_years accordingly and max_years to null. "
            "If it specifies 'fresher' or 'entry level', set min_years to 0 and max_years to null. "
            "If no specific years of experience are required or mentioned, set both min_years and max_years to null and experience_years strictly to 'Not specified'. "
            "Do NOT assume, default, or invent any years of experience. "
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "required_skills": ["string"],\n'
            '  "preferred_skills": ["string"],\n'
            '  "languages": ["string"],\n'
            '  "frameworks": ["string"],\n'
            '  "databases": ["string"],\n'
            '  "tools": ["string"],\n'
            '  "cloud": ["string"],\n'
            '  "responsibilities": ["string"],\n'
            '  "qualifications": ["string"],\n'
            '  "experience_years": "string",\n'
            '  "min_years": 0,\n'
            '  "max_years": 0,\n'
            '  "soft_skills": ["string"]\n'
            "}\n\n"
            f"Job Description:\n{raw_jd_text}"
        )

        det_min, det_max, det_range = parse_jd_experience(raw_jd_text)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                    },
                )
                if response.status_code == 200:
                    result_json = response.json()
                    response_text = result_json.get("response", "{}")
                    parsed_dict = json.loads(response_text)
                    if parsed_dict.get("required_skills") or parsed_dict.get("responsibilities"):
                        # Deterministic parser overrides LLM value when it finds a pattern
                        if det_min is not None:
                            parsed_dict["min_years"] = det_min
                            parsed_dict["max_years"] = det_max
                            parsed_dict["experience_range"] = det_range
                            parsed_dict["experience_years"] = det_range
                        else:
                            if "experience_range" not in parsed_dict:
                                parsed_dict["experience_range"] = parsed_dict.get("experience_years")
                        # Augment categories with deterministic keywords from the JD
                        det = self.deterministic_jd_extraction(raw_jd_text)
                        for cat in ["languages", "frameworks", "databases", "tools", "cloud"]:
                            existing = set(parsed_dict.get(cat, []))
                            for item in getattr(det, cat, []):
                                if item not in existing:
                                    parsed_dict.setdefault(cat, []).append(item)
                        return StructuredJDAnalysis(**parsed_dict)
        except Exception:
            pass

        return self.deterministic_jd_extraction(raw_jd_text)

    def deterministic_jd_extraction(self, text: str) -> StructuredJDAnalysis:
        """Deterministic keyword extraction fallback guaranteeing accurate, non-hallucinated analysis."""
        text_lower = text.lower()
        extracted: Dict[str, List[str]] = {cat: [] for cat in TECH_CATEGORIES}

        # Check line by line to determine required vs preferred context
        raw_lines = [line.strip("-•* ").strip() for line in text.splitlines() if line.strip()]
        req_set = []
        pref_set = []

        pref_triggers = ["prefer", "preferred", "nice to have", "good to have", "plus", "optional", "bonus", "advantage"]

        for line in raw_lines:
            ll = line.lower()
            is_pref_line = any(trig in ll for trig in pref_triggers)
            target_list = pref_set if is_pref_line else req_set

            # Check special contextual phrases
            if "code language" in ll or "coding language" in ll:
                target_list.append("Coding / Scripting Languages")
            if "customer-facing" in ll or "customer facing" in ll:
                target_list.append("Customer-Facing Experience")

            for cat, keywords in TECH_CATEGORIES.items():
                for kw in keywords:
                    pattern = rf"\b{re.escape(kw)}\b"
                    if re.search(pattern, ll):
                        canonical = CANONICAL_NAMES.get(kw, kw.title())
                        if canonical not in extracted[cat]:
                            extracted[cat].append(canonical)
                        if canonical not in target_list:
                            target_list.append(canonical)

        # Global sweep for any keywords missed line-by-line
        for cat, keywords in TECH_CATEGORIES.items():
            for kw in keywords:
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, text_lower):
                    canonical = CANONICAL_NAMES.get(kw, kw.title())
                    if canonical not in extracted[cat]:
                        extracted[cat].append(canonical)
                    if canonical not in req_set and canonical not in pref_set:
                        req_set.append(canonical)

        # Extract experience years using deterministic parser
        min_years, max_years, exp_range = parse_jd_experience(text)
        experience_years = exp_range if exp_range else "Not specified"

        # Split lines for responsibilities and qualifications
        responsibilities = []
        qualifications = []

        is_resp = False
        is_qual = False

        for line in raw_lines:
            line_l = line.lower()
            if "responsibilit" in line_l or "what you'll do" in line_l or "duties" in line_l or "role:" in line_l:
                is_resp = True
                is_qual = False
                continue
            elif "qualification" in line_l or "requirement" in line_l or "what we look for" in line_l or "eligibility" in line_l:
                is_qual = True
                is_resp = False
                continue

            if is_resp and len(line) > 10 and len(responsibilities) < 10:
                responsibilities.append(line)
            elif is_qual and len(line) > 10 and len(qualifications) < 10:
                qualifications.append(line)

        # Fallback if specific section headers were absent
        if not responsibilities:
            responsibilities = [l for l in raw_lines if len(l) > 25 and not any(q in l.lower() for q in ["degree", "b.tech", "b.e", "qualification"])][:6]
        if not qualifications:
            qualifications = [l for l in raw_lines if any(q in l.lower() for q in ["degree", "b.tech", "b.e", "b.sc", "qualification", "experience", "prefer"])][:5]

        # Combine technical skills into required/preferred
        # Ensure SQL and Database Server appear prioritized if in JD
        req_deduped = []
        for s in req_set:
            if s not in req_deduped:
                req_deduped.append(s)

        pref_deduped = []
        for s in pref_set:
            if s not in pref_deduped and s not in req_deduped:
                pref_deduped.append(s)

        return StructuredJDAnalysis(
            required_skills=req_deduped,
            preferred_skills=pref_deduped,
            languages=sorted(list(set(extracted["languages"]))),
            frameworks=sorted(list(set(extracted["frameworks"]))),
            databases=sorted(list(set(extracted["databases"] + extracted["concepts"]))),
            tools=sorted(list(set(extracted["tools"]))),
            cloud=sorted(list(set(extracted["cloud"]))),
            responsibilities=responsibilities,
            qualifications=qualifications,
            experience_years=experience_years,
            min_years=min_years,
            max_years=max_years,
            experience_range=exp_range,
            soft_skills=sorted(list(set(extracted["soft_skills"]))),
        )

    def check_unsupported_evidence(
        self,
        suggested_text: str,
        candidate_evidence: Optional[Dict[str, Any]] = None,
        context_skills: Optional[List[str]] = None,
        current_text: str = "",
    ) -> List[str]:
        """Detects technical skills or claims present in suggested_text that are not backed
        by candidate verified evidence or the current section text.
        """
        if not suggested_text:
            return []

        # Gather all verified tokens and phrases
        verified_corpus = set()

        if context_skills:
            for s in context_skills:
                verified_corpus.add(s.strip().lower())

        if candidate_evidence:
            for s in candidate_evidence.get("skills", []):
                verified_corpus.add(s.strip().lower())
            for exp in candidate_evidence.get("experience", []):
                for token in re.findall(r"\b[A-Za-z0-9\.\+#\-]+\b", str(exp).lower()):
                    verified_corpus.add(token)
            for proj in candidate_evidence.get("projects", []):
                for token in re.findall(r"\b[A-Za-z0-9\.\+#\-]+\b", str(proj).lower()):
                    verified_corpus.add(token)
            for cert in candidate_evidence.get("certifications", []):
                for token in re.findall(r"\b[A-Za-z0-9\.\+#\-]+\b", str(cert).lower()):
                    verified_corpus.add(token)
            for edu in candidate_evidence.get("education", []):
                for token in re.findall(r"\b[A-Za-z0-9\.\+#\-]+\b", str(edu).lower()):
                    verified_corpus.add(token)

        if current_text:
            for token in re.findall(r"\b[A-Za-z0-9\.\+#\-]+\b", current_text.lower()):
                verified_corpus.add(token)

        # Detect technical skills in suggested_text
        suggested_lower = suggested_text.lower()
        unsupported = []

        for cat, keywords in TECH_CATEGORIES.items():
            for kw in keywords:
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, suggested_lower):
                    canonical = CANONICAL_NAMES.get(kw, kw.title())
                    # Check if present in verified corpus
                    is_verified = (
                        kw in verified_corpus
                        or canonical.lower() in verified_corpus
                        or any(kw in v for v in verified_corpus if len(v) > 2)
                    )
                    if not is_verified and canonical not in unsupported:
                        unsupported.append(canonical)

        return unsupported

    async def refine_section(
        self,
        section: str,
        instruction: str,
        current_text: str,
        candidate_evidence: Optional[Dict[str, Any]] = None,
        context_skills: Optional[List[str]] = None,
        acknowledge_unsupported: bool = False,
    ) -> Dict[str, Any]:
        """Refines resume section content using Ollama following the candidate's custom prompt,
        with strict anti-fabrication evidence checking and fallback.
        """
        evidence_summary_lines = []
        if context_skills:
            evidence_summary_lines.append(f"Verified Skills: {', '.join(context_skills)}")
        if candidate_evidence:
            if candidate_evidence.get("experience"):
                evidence_summary_lines.append(f"Experience: {'; '.join(candidate_evidence['experience'][:3])}")
            if candidate_evidence.get("projects"):
                evidence_summary_lines.append(f"Projects: {'; '.join(candidate_evidence['projects'][:3])}")
            if candidate_evidence.get("certifications"):
                evidence_summary_lines.append(f"Certifications: {'; '.join(candidate_evidence['certifications'])}")

        evidence_summary = "\n".join(evidence_summary_lines) if evidence_summary_lines else "None provided."

        prompt = (
            "You are an expert resume assistant and career coach.\n"
            "Your highest priority is to faithfully follow the candidate's instruction.\n\n"
            f"Candidate Instruction: {instruction}\n"
            f"Target Section: {section}\n"
            f"Current Content:\n{current_text or '(None)'}\n\n"
            f"Verified Candidate Evidence Context:\n{evidence_summary}\n\n"
            "Guidelines:\n"
            "1. Execute the candidate's instruction directly and completely. Do not replace it with predefined templates.\n"
            "2. Ground qualifications, technical skills, and achievements in the candidate's verified evidence whenever possible.\n"
            "3. If the user asks for feedback, critique, or advice, return that constructive feedback clearly in suggested_text.\n"
            "4. Return strictly a valid JSON object matching this schema:\n"
            '{\n  "suggested_text": "string",\n  "explanation": "string"\n}'
        )

        suggested_text = ""
        explanation = ""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                        "keep_alive": "15m",
                    },
                )
                if response.status_code == 200:
                    result_json = response.json()
                    response_text = result_json.get("response", "{}")
                    parsed_dict = json.loads(response_text)
                    if "suggested_text" in parsed_dict and parsed_dict["suggested_text"]:
                        suggested_text = parsed_dict["suggested_text"]
                        explanation = parsed_dict.get("explanation", f"Applied instruction: {instruction}")
        except Exception:
            pass

        # If Ollama didn't return a valid revision, use deterministic fallback responsive to instruction
        if not suggested_text:
            fallback = self.deterministic_refine_section(section, instruction, current_text)
            suggested_text = fallback["suggested_text"]
            explanation = fallback["explanation"]

        # Anti-fabrication check: detect unsupported claims
        unsupported = self.check_unsupported_evidence(
            suggested_text=suggested_text,
            candidate_evidence=candidate_evidence,
            context_skills=context_skills,
            current_text=current_text,
        )

        has_unsupported = len(unsupported) > 0
        warning = None

        if has_unsupported:
            if not acknowledge_unsupported:
                warning = (
                    f"This revision introduces technical claims or skills not found in your verified profile: "
                    f"{', '.join(unsupported)}. Please acknowledge to proceed with this unverified content."
                )

        return {
            "suggested_text": suggested_text,
            "explanation": explanation,
            "has_unsupported_content": has_unsupported,
            "missing_evidence": unsupported,
            "evidence_warning": warning,
        }

    def deterministic_refine_section(self, section: str, instruction: str, current_text: str) -> Dict[str, str]:
        """Deterministic section refinement fallback that responds intelligently to user instructions."""
        inst = (instruction or "").lower().strip()
        lines = [line.strip() for line in (current_text or "").splitlines() if line.strip()]
        action_verbs = ["Architected", "Engineered", "Implemented", "Streamlined", "Optimized", "Spearheaded", "Delivered"]

        # 1. Feedback / critique instruction
        if any(w in inst for w in ["feedback", "critique", "review", "evaluate", "assessment"]):
            if current_text and len(current_text.strip()) > 10:
                suggested = (
                    f"Section Feedback for '{section}':\n"
                    f"1. Strengths: Content clearly states technical duties and functional scope.\n"
                    f"2. Clarity: Tone is direct, but could be enhanced with specific quantified impact (e.g., % improvement, latency reduction).\n"
                    f"3. Recommendation: Align phrasing closely with key job requirements while preserving verified facts."
                )
            else:
                suggested = (
                    f"Section Feedback for '{section}': Currently empty. Recommend outlining core responsibilities, "
                    f"verified technologies, and measurable achievements aligned with target roles."
                )
            return {
                "suggested_text": suggested,
                "explanation": "Provided constructive review and feedback on section content and alignment.",
            }

        # 2. Bullet points request
        if any(w in inst for w in ["bullet", "bullets", "list", "convert to bullet"]):
            if lines:
                refined_lines = []
                for i, line in enumerate(lines):
                    clean = line.lstrip("-•* ").strip()
                    words = clean.split()
                    if words and not words[0].endswith("ed"):
                        verb = action_verbs[i % len(action_verbs)]
                        clean = f"{verb} {clean[0].lower() + clean[1:] if len(clean) > 1 else clean}"
                    refined_lines.append(f"• {clean}")
                suggested = "\n".join(refined_lines)
            elif current_text:
                # Split sentences into bullets
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", current_text) if s.strip()]
                suggested = "\n".join(f"• {s}" for s in sentences)
            else:
                suggested = f"• Implemented scalable engineering solutions aligned with verified competencies."
            return {
                "suggested_text": suggested,
                "explanation": f"Converted {section} into structured action-oriented bullet points.",
            }

        # 3. Concise / shorten request
        if any(w in inst for w in ["concise", "shorten", "brief", "one line", "single sentence", "tighten"]):
            if current_text:
                first_sentence = re.split(r"(?<=[.!?])\s+", current_text.strip())[0]
                suggested = first_sentence.strip()
            else:
                suggested = "Experienced software engineer dedicated to delivering high-performance, reliable systems."
            return {
                "suggested_text": suggested,
                "explanation": f"Condensed {section} into concise, impactful phrasing.",
            }

        # 4. Simpler / plain language request
        if any(w in inst for w in ["simpler", "simple", "plain", "clear language", "plain english"]):
            if current_text:
                simplified = current_text.replace("Spearheaded", "Led").replace("Architected", "Designed").replace("Utilized", "Used")
                suggested = simplified
            else:
                suggested = "Software developer who builds reliable applications and improves team workflows."
            return {
                "suggested_text": suggested,
                "explanation": f"Rewrote {section} in clear, straightforward language without unnecessary jargon.",
            }

        # 5. Professional tone / action verbs
        if lines:
            refined_lines = []
            for i, line in enumerate(lines):
                clean = line.lstrip("-•* ").strip()
                words = clean.split()
                if words and not words[0].endswith("ed"):
                    verb = action_verbs[i % len(action_verbs)]
                    clean = f"{verb} {clean[0].lower() + clean[1:] if len(clean) > 1 else clean}"
                refined_lines.append(clean)
            suggested = "\n".join(refined_lines)
            explanation = f"Refined {section} with professional action verbs and active cadence."
        elif current_text:
            suggested = current_text.strip()
            explanation = f"Polished {section} phrasing based on requested instruction."
        else:
            suggested = "Results-driven engineering professional focused on reliable system implementation and continuous delivery."
            explanation = f"Generated professional baseline for {section}."

        return {
            "suggested_text": suggested,
            "explanation": explanation,
        }

    async def categorize_skills_batch(
        self, items: List[Tuple[str, Optional[str]]], valid_categories: List[str]
    ) -> Dict[str, str]:
        """Categorizes candidate skills into standard categories using taxonomy or Ollama."""
        results: Dict[str, str] = {}
        valid_set = set(valid_categories)
        unmatched = []

        for skill, hint in items:
            skill_l = skill.lower().strip()
            matched_cat = None
            for cat, keywords in TECH_CATEGORIES.items():
                if skill_l in keywords:
                    if cat == "languages" and "Languages" in valid_set:
                        matched_cat = "Languages"
                    elif cat == "frameworks" and "Frameworks" in valid_set:
                        matched_cat = "Frameworks"
                    elif cat == "databases" and "Databases" in valid_set:
                        matched_cat = "Databases"
                    elif cat in ("cloud", "tools"):
                        for vc in valid_categories:
                            if "cloud" in vc.lower() or "tools" in vc.lower():
                                matched_cat = vc
                                break
                    break
            if matched_cat:
                results[skill] = matched_cat
            else:
                unmatched.append(skill)

        if unmatched:
            prompt = (
                f"Categorize each of these skills into one of the allowed categories: {', '.join(valid_categories)}.\n"
                f"Skills: {', '.join(unmatched)}\n"
                "Return JSON mapping skill to category, e.g. {\"Docker\": \"Cloud & Infrastructure\"}."
            )
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(
                        f"{self.base_url}/api/generate",
                        json={"model": self.model, "prompt": prompt, "stream": False, "format": "json", "keep_alive": "15m"},
                    )
                    if resp.status_code == 200:
                        mapped = json.loads(resp.json().get("response", "{}"))
                        for k, v in mapped.items():
                            if v in valid_set:
                                results[k] = v
            except Exception:
                pass

        for s in unmatched:
            if s not in results:
                results[s] = "Other" if "Other" in valid_set else valid_categories[-1]

        return results

    async def extract_skills_from_chunk(self, chunk_text: str) -> List[str]:
        """Extracts technical skills from text chunk using taxonomy and Ollama."""
        extracted = []
        chunk_lower = chunk_text.lower()
        for cat, keywords in TECH_CATEGORIES.items():
            for kw in keywords:
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, chunk_lower):
                    extracted.append(CANONICAL_NAMES.get(kw, kw.title()))
        return list(dict.fromkeys(extracted))


ollama_provider = OllamaProvider()
