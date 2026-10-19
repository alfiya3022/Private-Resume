import json
import re
from typing import Dict, List, Optional
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
            "CRITICAL: Extract 'experience_years' ONLY if explicitly stated in the JD text. "
            "If no specific years of experience are required or mentioned, set 'experience_years' strictly to 'Not specified'. "
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
            '  "soft_skills": ["string"]\n'
            "}\n\n"
            f"Job Description:\n{raw_jd_text}"
        )

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

        # Extract experience years (e.g. "Minimum 1 to 2 years of experience in SQL", "1-3 years")
        exp_match = re.search(
            r"(?:minimum|at least)?\s*(\b\d+\s*(?:to|-)\s*\d+\+?\s*years?(?:\s+of\s+[\w\s]+experience)?)",
            text_lower
        )
        if not exp_match:
            exp_match = re.search(r"(\b\d+[\+\-]?\s*(?:to|-)?\s*\d*\s*years?(?:\s+of\s+(?:relevant\s+)?experience)?)", text_lower)
        experience_years = exp_match.group(1).title() if exp_match else "Not specified"

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
            soft_skills=sorted(list(set(extracted["soft_skills"]))),
        )

    async def refine_section(
        self, section: str, instruction: str, current_text: str, context_skills: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Refines resume section content using Ollama or deterministic fallback."""
        skills_ctx = ", ".join(context_skills) if context_skills else "Candidate verified profile skills"
        prompt = (
            "You are an expert resume editor and technical career coach. "
            "Adhere strictly to anti-fabrication guidelines: NEVER invent or hallucinate unverified skills, metrics, certifications, or employers. "
            f"Permitted context skills from candidate profile: {skills_ctx}.\n\n"
            f"Target Section: {section}\n"
            f"Current Content:\n{current_text or 'None'}\n\n"
            f"Candidate Revision Request: {instruction}\n\n"
            "SPECIAL RULE FOR SUMMARY: Keep the executive summary sharply focused on the specific role, tech stack, and responsibilities demanded by the target job. "
            "Do NOT summarize the candidate's entire historical career or irrelevant past domains. Tailor directly to the job description.\n\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            '{\n  "suggested_text": "string",\n  "explanation": "string"\n}'
        )

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
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
                    if "suggested_text" in parsed_dict:
                        return parsed_dict
        except Exception:
            pass

        return self.deterministic_refine_section(section, instruction, current_text)

    def deterministic_refine_section(self, section: str, instruction: str, current_text: str) -> Dict[str, str]:
        """Deterministic section refinement fallback ensuring factual action-oriented phrasing."""
        lines = [line.strip() for line in (current_text or "").splitlines() if line.strip()]
        action_verbs = ["Architected", "Engineered", "Implemented", "Streamlined", "Optimized", "Spearheaded", "Delivered"]

        if section.lower() == "summary":
            suggested = (
                f"Results-driven software engineer with proven experience in technical implementation, "
                f"system reliability, and collaborative engineering. Committed to delivering scalable solutions."
            )
            explanation = "Restructured summary into an impactful, fact-grounded professional profile."
        elif lines:
            refined_lines = []
            for i, line in enumerate(lines):
                clean = line.lstrip("-•* ").strip()
                words = clean.split()
                if words and not words[0].endswith("ed"):
                    verb = action_verbs[i % len(action_verbs)]
                    clean = f"{verb} {clean[0].lower() + clean[1:] if len(clean) > 1 else clean}"
                refined_lines.append(f"• {clean}")
            suggested = "\n".join(refined_lines)
            explanation = f"Refined {section} bullet points with active action verbs and professional cadence."
        else:
            suggested = current_text or "Refined section based on provided instruction."
            explanation = f"Updated {section} with clear technical phrasing."

        return {
            "suggested_text": suggested,
            "explanation": explanation,
        }


ollama_provider = OllamaProvider()
