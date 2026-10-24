import json
import re
from typing import Dict, List, Optional, Any, Tuple
import httpx
from app.core.config import settings
from app.schemas.analysis import StructuredJDAnalysis
from app.services.ai.resume_llm_schemas import (
    LLMResumeExtraction,
    LLMChunkSkills,
    LLMSkillCategoryBatch,
)

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
        
    async def extract_full_resume_structure(
        self, text: str, available_links: Optional[List[str]] = None
    ) -> Optional[LLMResumeExtraction]:
        """Extracts complete resume structure via Ollama with strict factual preservation."""

        if not text or not text.strip():
            return None

        links_ctx = (
            "\n".join(f"- {link}" for link in available_links)
            if available_links
            else "None"
        )

        prompt = f"""
You are an expert resume parser and information extraction system.

Your task is to extract the complete, factual structure of a resume.
The resume may come from any template, country, academic system, profession,
or document layout.

The input may contain:
- Different section headings
- Merged or wrapped lines
- Bullets represented by symbols, dashes, or plain text
- Dates in different formats
- Contact information in headers or footers
- Academic scores expressed as CGPA, GPA, percentages, marks, or other grading systems
- Projects embedded inside experience sections
- Technologies mentioned inside descriptions rather than technology lists
- Sections appearing in an unusual order

Understand the MEANING of the content. Do not rely only on section headings.

OUTPUT CONTRACT
Return exactly one valid JSON object matching this structure:

{{
  "personal_info": {{
    "name": null,
    "email": null,
    "phone": null,
    "location": null,
    "headline": null,
    "linkedin_url": null,
    "github_url": null,
    "portfolio_url": null
  }},
  "summary": null,
  "education": [],
  "experience": [],
  "projects": [],
  "certifications": []
}}

GENERAL RULES

1. Extract only information supported by the resume text.
2. Never invent, guess, or silently correct information.
3. Preserve names, titles, organization names, dates, grades, technologies,
   metrics, and URLs as written wherever possible.
4. Do not discard information merely because it appears in an unusual location.
5. Do not confuse the candidate's information with another person's information.
6. Do not confuse a company, institution, city, project, or job title with
   the candidate's name.
7. If a field is unavailable, use null.
8. If a section has no entries, return an empty list.
9. Preserve the order in which entries appear in the resume.
10. Do not create a skills list. Skills extraction is handled separately.

PERSONAL INFORMATION

Extract:
- Candidate's full name
- Email address
- Phone number
- Location
- Professional headline
- LinkedIn URL
- GitHub URL
- Portfolio or personal website URL

Contact details may appear in headers, footers, contact sections, or inline text.

Do not mistake a company's contact information for the candidate's information.

Only extract a URL when it clearly belongs to the candidate.
Do not construct URLs from usernames or platform names.

EDUCATION

Return one object for each distinct degree, qualification, or educational
institution entry.

Each object must contain:
- institution
- degree
- field_of_study
- grade
- start_date
- end_date

ACADEMIC GRADES AND SCORES

This is a critical requirement.

Extract every academic score associated with an education entry, including:
- CGPA
- GPA
- Percentage
- Marks
- Grade
- Classification
- Other grading systems

Preserve the score and its grading scale together.

Examples:
- "8.2 CGPA" must remain "8.2 CGPA".
- "8.2/10" must remain "8.2/10".
- "85%" must remain "85%".
- "3.7 GPA out of 4.0" must retain the GPA and scale.
- "First Class with Distinction" must remain as written.

Do not convert CGPA to percentage.
Do not convert percentage to GPA.
Do not assume a grading scale.
Do not calculate a missing score.
Do not associate a score with the wrong degree or institution.

Store the complete grade or score expression in the "grade" field.

EDUCATION DATES

Preserve education dates exactly as written.

Examples:
- "2022 - 2026" should remain "2022 - 2026".
- "Aug 2022 - May 2026" should retain those dates.
- "2022 - Present" should not be converted into a guessed end year.

Associate dates with the correct education entry.
Do not mix dates from adjacent entries.

EXPERIENCE

Extract professional experience, employment, internships, freelance work,
and other relevant professional roles.

Return one object per distinct role.

Each object must contain:
- company
- title
- location
- start_date
- end_date
- is_current
- description
- bullets

If a company has multiple roles, return separate objects for those roles.

EXPERIENCE DATES

Preserve the date text exactly as written.

Examples:
- "Jan 2025 - Mar 2025"
- "2024 - Present"
- "June 2023 - August 2023"
- "01/2024 - 06/2024"

Do not normalize date formats.
Do not infer a missing month or year.
Do not use dates from another role.
Do not confuse a project date with an employment date.

For date ranges:
- start_date contains the starting date expression.
- end_date contains the ending date expression.

For an explicitly ongoing role:
- Set is_current to true.
- Preserve the original end-date wording, such as "Present", when applicable.

For a role that is not explicitly ongoing:
- Set is_current to false.

Do not mark a role as current merely because it is the most recent role.

EXPERIENCE DESCRIPTIONS AND BULLETS

Preserve the factual meaning of descriptions and bullets.

Do not rewrite accomplishments into stronger claims.
Do not invent metrics, responsibilities, technologies, or outcomes.

Only join lines when they are clearly wrapped parts of the same bullet.

Keep separate bullets separate.

PROJECTS

Extract personal, academic, professional, and side projects.

Return one object per distinct project.

Each object must contain:
- title
- role
- description
- bullets
- technologies
- url
- github_url
- live_url
- start_date
- end_date

PROJECT IDENTIFICATION

A project may be identified by:
- A project section heading
- A title followed by a description
- A title followed by technologies
- A title followed by dates
- A project link
- Context indicating that the content describes a project

Do not require a project to appear under a heading named "Projects".

Do not confuse a project with an employer or job title.

PROJECT BOUNDARIES

Every project bullet belongs only to its correct project.

Use the nearest relevant project title and surrounding context.

Never:
- Merge two separate projects
- Put a project title inside a bullet
- Copy a bullet into multiple projects
- Move project content into employment experience
- Move employment responsibilities into a project

TECHNOLOGIES

Extract technologies explicitly associated with the project.

Technologies may appear in:
- A technology stack line
- Project descriptions
- Project bullets
- Other nearby text that clearly describes the project

Do not infer a technology solely because it is common for that kind of project.

Do not add technologies that are not supported by the resume.

PROJECT DATES

Preserve project dates exactly as written.

Associate each date with the correct project.

Do not use employment dates as project dates.
Do not invent dates when none are stated.

PROJECT LINKS

Use the provided document links only when a link clearly belongs to a project.

A GitHub link should populate github_url.
A live project link should populate live_url.
Other clearly associated project URLs may populate url.

Do not guess which project a link belongs to.

CERTIFICATIONS

Extract certifications, courses, awards, achievements, publications,
and competition results.

Return one object per distinct item.

Each object must contain:
- name
- issuer
- issue_date
- credential_url

Preserve certification names, issuers, dates, and URLs as written.

Do not confuse a course with a certification unless the resume identifies
it as a course or credential.

Do not invent an issuer or credential URL.

DATE ASSOCIATION AND ACCURACY

Dates are especially important.

For every entry:
1. Identify the date expression.
2. Identify the entry it belongs to.
3. Preserve the original date wording.
4. Keep start and end dates in their correct fields.
5. Do not use a date from a neighboring entry.
6. Do not infer missing dates.
7. Do not silently convert date formats.

If a date is ambiguous, preserve only what the text supports.
Do not guess.

SUMMARY

Extract the candidate's existing professional summary or profile statement.

Do not generate a new summary.
Do not rewrite the candidate's summary.
If no summary exists, return null.

FINAL VALIDATION

Before returning the JSON:

- Confirm that personal information has been extracted when present.
- Confirm that all education entries are included.
- Confirm that academic scores and grading scales are preserved.
- Confirm that all experience roles are included.
- Confirm that experience dates are associated with the correct roles.
- Confirm that ongoing roles are identified only when explicitly supported.
- Confirm that all projects are included separately.
- Confirm that project technologies are grounded in the resume.
- Confirm that certification dates and issuers are not mixed.
- Confirm that no unsupported information was added.
- Confirm that the output matches the requested JSON structure.

Return JSON only. Do not include Markdown fences, explanations, or commentary.

DOCUMENT LINKS
These links may be used only when they clearly belong to a project:

{links_ctx}

RESUME TEXT
{text}
"""

        for attempt in range(2):
            try:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.0,
                        "num_ctx": 8192,
                    },
                    "think": False,
                }

                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                    )

                    response.raise_for_status()

                    result_json = response.json()
                    response_text = result_json.get("response", "{}")
                    parsed = json.loads(response_text)

                    validated = LLMResumeExtraction.model_validate(parsed)
                    return validated

            except (
                httpx.HTTPError,
                json.JSONDecodeError,
                ValueError,
                TypeError,
            ):
                if attempt == 1:
                    return None

        return None

    async def extract_skills_from_chunk(self, chunk: str) -> List[str]:
        """Extracts skills from a single text chunk via Ollama."""
        prompt = (
            "Extract every individual skill mentioned in this part of a resume. Skills can appear anywhere: "
            "a skills list, a project technology line, a job description, a bullet point or a summary sentence. "
            "The resume can be from any field (technology, finance, HR, marketing, operations and so on).\n"
            "Rules:\n"
            "- One skill per item. Split brackets: \"SQL (MS SQL Server, T-SQL)\" becomes SQL, MS SQL Server, T-SQL.\n"
            "- Keep multi-word skills together, for example \"Exploratory Data Analysis\".\n"
            "- Include tools, software, programming languages, frameworks, platforms, methods and domain skills. Include soft skills only when they are explicitly listed as skills.\n"
            "- Do NOT include the candidate's name, company names, project names, school names, degrees, job titles, or level words such as \"Basics\" or \"Advanced\".\n"
            "- Only include skills written in the text. Never add any.\n"
            f"TEXT:\n{chunk}"
        )
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.0,
                    "num_ctx": 8192,
                },
                "think": False,
            }
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                if response.status_code == 200:
                    res_json = response.json()
                    resp_text = res_json.get("response", "{}")
                    parsed = json.loads(resp_text)
                    if isinstance(parsed, list):
                        return [str(s) for s in parsed if s]
                    if isinstance(parsed, dict):
                        skills_list = parsed.get("skills") or parsed.get("items") or []
                        if isinstance(skills_list, list):
                            return [str(s) for s in skills_list if s]
        except Exception:
            pass
        return []

    async def categorize_skills_batch(
        self, batch: List[tuple[str, Optional[str]]], categories: List[str]
    ) -> Dict[str, str]:
        """Categorizes a batch of up to 30 skills against a fixed taxonomy via Ollama."""
        categories_str = ", ".join(categories)
        lines = "\n".join(
            f"{skill} | {hint}" if hint else f"{skill} | "
            for skill, hint in batch
        )
        prompt = (
            f"Assign each skill to exactly one category from this list: {categories_str}.\n"
            "Choose by what the skill really is: pick a technology category for technology skills, and a non-technology category for business, finance, HR, sales, design, operations, or people skills. "
            "Some skills have a hint: the label the resume itself used for that skill. Use the hint only as a clue, not as the answer. "
            "If nothing fits, use \"Other\". Return every skill given, spelled exactly as given.\n"
            "Skills (format: skill | hint):\n"
            f"{lines}"
        )
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.0,
                    "num_ctx": 8192,
                },
                "think": False,
            }
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                if response.status_code == 200:
                    res_json = response.json()
                    resp_text = res_json.get("response", "{}")
                    parsed = json.loads(resp_text)
                    cat_map: Dict[str, str] = {}
                    items = []
                    if isinstance(parsed, list):
                        items = parsed
                    elif isinstance(parsed, dict):
                        items = parsed.get("items") or parsed.get("skills") or []
                    for item in items:
                        if isinstance(item, dict):
                            s = item.get("skill") or item.get("name")
                            c = item.get("category")
                            if s and c:
                                cat_map[str(s).strip()] = str(c).strip()
                    return cat_map
        except Exception:
            pass
        return {}


ollama_provider = OllamaProvider()
