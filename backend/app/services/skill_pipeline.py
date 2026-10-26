import re
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from rapidfuzz import fuzz
from app.services.ai.resume_llm_schemas import LLMChunkSkills, LLMSkillCategoryBatch
from app.services.career_knowledge_service import KNOWN_TECH_ALIASES, normalize_term
from app.core.diagnostics import logger

FIXED_SKILL_CATEGORIES: List[str] = [
    "Programming Language",
    "Languages",
    "Frontend",
    "Frontend Framework",
    "Backend",
    "Backend Framework",
    "Full Stack",
    "Mobile",
    "Database",
    "Cloud",
    "DevOps",
    "DevOps & Tools",
    "AI & Machine Learning",
    "Data Science & Analytics",
    "Data & Analytics",
    "Testing & QA",
    "Security",
    "Networking",
    "Tools & Platforms",
    "Methodologies & Practices",
    "Architecture & Systems",
    "Finance & Accounting",
    "HR & Recruitment",
    "Sales & Marketing",
    "Design",
    "Operations & Management",
    "Soft Skills",
    "Uncategorized",
    "Other",
]

LABEL_CATEGORY_MAP: Dict[str, str] = {
    "programming languages": "Programming Language",
    "programming language": "Programming Language",
    "coding": "Programming Language",
    "languages": "Languages",
    "language": "Languages",
    "spoken languages": "Languages",
    "natural languages": "Languages",
    "language competencies": "Languages",
    "frontend": "Frontend",
    "front-end": "Frontend",
    "web technologies": "Frontend",
    "web development": "Frontend",
    "web": "Frontend",
    "backend": "Backend",
    "back-end": "Backend",
    "server-side": "Backend",
    "frameworks & libraries": "Backend Framework",
    "frameworks and libraries": "Backend Framework",
    "frameworks": "Backend Framework",
    "libraries": "Backend Framework",
    "databases": "Database",
    "database": "Database",
    "database management": "Database",
    "rdbms": "Database",
    "cloud": "Cloud",
    "cloud platforms": "Cloud",
    "cloud technologies": "Cloud",
    "devops": "DevOps",
    "devops & tools": "DevOps & Tools",
    "devops and tools": "DevOps & Tools",
    "ci/cd": "DevOps",
    "tools": "Tools & Platforms",
    "tools & platforms": "Tools & Platforms",
    "developer tools": "Tools & Platforms",
    "software & tools": "Tools & Platforms",
    "platforms": "Tools & Platforms",
    "utilities": "Tools & Platforms",
    "data science & analytics": "Data Science & Analytics",
    "data science": "Data Science & Analytics",
    "data analytics": "Data Science & Analytics",
    "analytics": "Data Science & Analytics",
    "data & analytics": "Data Science & Analytics",
    "business intelligence": "Data Science & Analytics",
    "bi": "Data Science & Analytics",
    "machine learning": "AI & Machine Learning",
    "ai & machine learning": "AI & Machine Learning",
    "artificial intelligence": "AI & Machine Learning",
    "deep learning": "AI & Machine Learning",
    "testing": "Testing & QA",
    "testing & qa": "Testing & QA",
    "qa": "Testing & QA",
    "security": "Security",
    "cybersecurity": "Security",
    "methodologies": "Methodologies & Practices",
    "methodologies & practices": "Methodologies & Practices",
    "practices": "Methodologies & Practices",
    "soft skills": "Soft Skills",
    "interpersonal skills": "Soft Skills",
}

KNOWN_SKILL_CATEGORIES: Dict[str, str] = {
    # Programming Languages
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
    "sql": "Programming Language",
    "t-sql": "Programming Language",
    "tsql": "Programming Language",
    "transact-sql": "Programming Language",
    "pl/sql": "Programming Language",
    "plsql": "Programming Language",
    "bash": "Programming Language",
    "powershell": "Programming Language",
    "shell": "Programming Language",
    "r": "Programming Language",
    "scala": "Programming Language",
    "dart": "Programming Language",
    "kotlin": "Programming Language",
    "swift": "Programming Language",
    "html": "Programming Language",
    "css": "Programming Language",
    
    # Frontend / Frameworks
    "react": "Frontend",
    "react.js": "Frontend",
    "reactjs": "Frontend",
    "next.js": "Frontend",
    "nextjs": "Frontend",
    "vue": "Frontend",
    "vue.js": "Frontend",
    "vuejs": "Frontend",
    "angular": "Frontend",
    "angularjs": "Frontend",
    "tailwind": "Frontend",
    "tailwind css": "Frontend",
    "bootstrap": "Frontend",
    "html5": "Frontend",
    "css3": "Frontend",
    "sass": "Frontend",
    "scss": "Frontend",
    "redux": "Frontend",
    "svelte": "Frontend",
    "jquery": "Frontend",

    # Backend / Frameworks
    "fastapi": "Backend Framework",
    "django": "Backend Framework",
    "flask": "Backend Framework",
    "express": "Backend Framework",
    "express.js": "Backend Framework",
    "spring": "Backend Framework",
    "spring boot": "Backend Framework",
    "node.js": "Backend",
    "nodejs": "Backend",
    "node": "Backend",
    ".net": "Backend Framework",
    "asp.net": "Backend Framework",
    "ruby on rails": "Backend Framework",
    "rails": "Backend Framework",
    "nestjs": "Backend Framework",

    # Databases
    "postgresql": "Database",
    "postgres": "Database",
    "pgsql": "Database",
    "mysql": "Database",
    "sqlite": "Database",
    "mongodb": "Database",
    "mongo": "Database",
    "redis": "Database",
    "elasticsearch": "Database",
    "sql server": "Database",
    "ms sql server": "Database",
    "microsoft sql server": "Database",
    "oracle": "Database",
    "oracle database": "Database",
    "dynamodb": "Database",
    "cassandra": "Database",
    "snowflake": "Database",
    "bigquery": "Database",
    "redshift": "Database",
    "couchdb": "Database",
    "neo4j": "Database",
    "mariadb": "Database",
    "rdbms": "Database",
    "nosql": "Database",
    "relational database": "Database",

    # Cloud
    "aws": "Cloud",
    "amazon web services": "Cloud",
    "azure": "Cloud",
    "microsoft azure": "Cloud",
    "gcp": "Cloud",
    "google cloud": "Cloud",
    "google cloud platform": "Cloud",
    "s3": "Cloud",
    "ec2": "Cloud",
    "lambda": "Cloud",
    "cloudformation": "Cloud",
    "terraform": "Cloud",

    # DevOps & Tools
    "docker": "DevOps & Tools",
    "kubernetes": "DevOps & Tools",
    "k8s": "DevOps & Tools",
    "jenkins": "DevOps & Tools",
    "git": "DevOps & Tools",
    "github": "DevOps & Tools",
    "gitlab": "DevOps & Tools",
    "bitbucket": "DevOps & Tools",
    "ci/cd": "DevOps & Tools",
    "cicd": "DevOps & Tools",
    "continuous integration": "DevOps & Tools",
    "continuous deployment": "DevOps & Tools",
    "linux": "DevOps & Tools",
    "ansible": "DevOps & Tools",
    "helm": "DevOps & Tools",
    "github actions": "DevOps & Tools",

    # AI & Machine Learning
    "machine learning": "AI & Machine Learning",
    "deep learning": "AI & Machine Learning",
    "pytorch": "AI & Machine Learning",
    "tensorflow": "AI & Machine Learning",
    "scikit-learn": "AI & Machine Learning",
    "sklearn": "AI & Machine Learning",
    "pandas": "AI & Machine Learning",
    "numpy": "AI & Machine Learning",
    "keras": "AI & Machine Learning",
    "nlp": "AI & Machine Learning",
    "natural language processing": "AI & Machine Learning",
    "computer vision": "AI & Machine Learning",
    "llm": "AI & Machine Learning",
    "large language models": "AI & Machine Learning",
    "hugging face": "AI & Machine Learning",
    "opencv": "AI & Machine Learning",
    "scipy": "AI & Machine Learning",

    # Data Science & Analytics
    "data analysis": "Data Science & Analytics",
    "exploratory data analysis": "Data Science & Analytics",
    "eda": "Data Science & Analytics",
    "data visualization": "Data Science & Analytics",
    "power bi": "Data Science & Analytics",
    "tableau": "Data Science & Analytics",
    "excel": "Data Science & Analytics",
    "microsoft excel": "Data Science & Analytics",
    "ms excel": "Data Science & Analytics",
    "ssis": "Data Science & Analytics",
    "ssrs": "Data Science & Analytics",
    "ssas": "Data Science & Analytics",
    "etl": "Data Science & Analytics",
    "data warehousing": "Data Science & Analytics",
    "data modeling": "Data Science & Analytics",
    "business intelligence": "Data Science & Analytics",
    "statistics": "Data Science & Analytics",

    # Tools & Platforms
    "jira": "Tools & Platforms",
    "confluence": "Tools & Platforms",
    "postman": "Tools & Platforms",
    "vs code": "Tools & Platforms",
    "visual studio": "Tools & Platforms",
    "visual studio code": "Tools & Platforms",
    "figma": "Tools & Platforms",
    "notion": "Tools & Platforms",
    "slack": "Tools & Platforms",
    "trello": "Tools & Platforms",
    "latex": "Tools & Platforms",
    "ftp": "Tools & Platforms",
    "sftp": "Tools & Platforms",
    "pgp": "Tools & Platforms",

    # Methodologies & Practices
    "agile": "Methodologies & Practices",
    "scrum": "Methodologies & Practices",
    "kanban": "Methodologies & Practices",
    "sdlc": "Methodologies & Practices",
    "rest api": "Methodologies & Practices",
    "rest apis": "Methodologies & Practices",
    "restful": "Methodologies & Practices",
    "restful api": "Methodologies & Practices",
    "restful apis": "Methodologies & Practices",
    "soap": "Methodologies & Practices",
    "microservices": "Methodologies & Practices",
    "unit testing": "Methodologies & Practices",
    "tdd": "Methodologies & Practices",
    "code review": "Methodologies & Practices",
    "design patterns": "Methodologies & Practices",

    # Soft Skills
    "communication": "Soft Skills",
    "teamwork": "Soft Skills",
    "leadership": "Soft Skills",
    "problem solving": "Soft Skills",
    "collaboration": "Soft Skills",
    "analytical thinking": "Soft Skills",
    "time management": "Soft Skills",
    "adaptability": "Soft Skills",
    "critical thinking": "Soft Skills",
    "mentoring": "Soft Skills",
    "client management": "Soft Skills",
}

LABEL_LINE_PATTERN = re.compile(
    r"^\s*(?:-\s*)?([A-Za-z][A-Za-z &/+.\-]{2,40}?)\s*:\s*(\S.*)$",
    re.MULTILINE,
)


def appears_in_source(value: Optional[str], source: Optional[str]) -> bool:
    """Checks whether an alphanumeric representation, alias, or fuzzy equivalent

    of value is grounded in the source text.
    """
    if not value or not source:
        return False
    clean_val = re.sub(r"[^a-zA-Z0-9]", "", str(value)).lower()
    clean_src = re.sub(r"[^a-zA-Z0-9]", "", str(source)).lower()
    if not clean_val:
        return False
    
    # 1. Direct alphanumeric substring
    if clean_val in clean_src:
        return True

    # 2. Known alias verification (e.g. Postgres <-> PostgreSQL, React <-> React.js)
    val_lower = str(value).strip().lower()
    meta = KNOWN_TECH_ALIASES.get(val_lower)
    if meta:
        canonical_clean = re.sub(r"[^a-zA-Z0-9]", "", meta["canonical"]).lower()
        if canonical_clean in clean_src:
            return True
        for alias in meta["aliases"]:
            alias_clean = re.sub(r"[^a-zA-Z0-9]", "", alias).lower()
            if alias_clean in clean_src:
                return True

    # 3. Multi-word phrase fuzzy matching
    if len(clean_val) >= 5:
        ratio = fuzz.partial_ratio(clean_val, clean_src)
        if ratio >= 88:
            return True

    return False


def find_source_evidence(skill: str, full_text: str) -> Optional[str]:
    """Locates the exact line or sentence where the skill appears in the resume."""
    if not skill or not full_text:
        return None
    skill_clean = skill.strip().lower()
    for line in full_text.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        if skill_clean in line_clean.lower() or appears_in_source(skill, line_clean):
            # Return trimmed line as evidence snippet (capped at 200 chars)
            return line_clean[:200]
    return None


class SkillPipeline:
    def __init__(self, ollama_provider=None):
        from app.services.ai.ollama_provider import ollama_provider as default_provider
        self.ollama_provider = ollama_provider or default_provider

    def split_into_chunks(self, text: str, max_chars: int = 3500) -> List[str]:
        """Splits text into chunks of roughly max_chars on line boundaries, never mid-line."""
        lines = text.splitlines(keepends=True)
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_len = 0

        for line in lines:
            line_len = len(line)
            if current_chunk and (current_len + line_len > max_chars):
                chunks.append("".join(current_chunk).strip())
                current_chunk = [line]
                current_len = line_len
            else:
                current_chunk.append(line)
                current_len += line_len

        if current_chunk:
            chunk_str = "".join(current_chunk).strip()
            if chunk_str:
                chunks.append(chunk_str)

        return chunks if chunks else [text.strip()]

    def extract_label_hints(self, text: str) -> List[tuple[str, str]]:
        """Finds label lines like 'Backend: Python, Node.js' and returns (label, right_hand_content)."""
        matches: List[tuple[str, str]] = []
        for match in LABEL_LINE_PATTERN.finditer(text):
            label = match.group(1).strip()
            content = match.group(2).strip()
            matches.append((label, content))
        return matches

    def match_hint_for_skill(self, skill: str, label_hints: List[tuple[str, str]]) -> Optional[str]:
        """Matches a skill to a label hint if the skill appears in the label's content."""
        clean_skill = re.sub(r"[^a-zA-Z0-9]", "", skill).lower()
        if not clean_skill:
            return None
        for label, content in label_hints:
            clean_content = re.sub(r"[^a-zA-Z0-9]", "", content).lower()
            if clean_skill in clean_content or appears_in_source(clean_skill, clean_content):
                return label
        return None

    def categorize_skill_deterministic(
        self, skill: str, hint: Optional[str] = None
    ) -> Optional[str]:
        """Deterministically classifies a skill using label hint and known taxonomy."""
        # 1. Check label hint first if available
        if hint:
            clean_hint = hint.lower().strip()
            if clean_hint in LABEL_CATEGORY_MAP:
                return LABEL_CATEGORY_MAP[clean_hint]
            for key, cat in LABEL_CATEGORY_MAP.items():
                if key in clean_hint:
                    return cat

        # 2. Check direct known skills taxonomy
        clean_skill = skill.lower().strip()
        if clean_skill in KNOWN_SKILL_CATEGORIES:
            return KNOWN_SKILL_CATEGORIES[clean_skill]

        # 3. Check canonical form via normalize_term
        norm = normalize_term(clean_skill).lower().strip()
        if norm in KNOWN_SKILL_CATEGORIES:
            return KNOWN_SKILL_CATEGORIES[norm]

        return None

    async def categorize_skills_hybrid(
        self,
        skills_with_hints: List[Tuple[str, Optional[str]]],
        full_text: str,
        correlation_id: Optional[str] = None,
    ) -> List[Dict[str, Optional[str]]]:
        """Categorizes skills using deterministic taxonomy first, falling back to Ollama
        only for ambiguous skills.
        """
        results: List[Dict[str, Optional[str]]] = []
        ambiguous_items: List[Tuple[str, Optional[str]]] = []
        valid_cats_set = set(FIXED_SKILL_CATEGORIES)

        for skill, hint in skills_with_hints:
            cat = self.categorize_skill_deterministic(skill, hint)
            if cat and cat in valid_cats_set:
                results.append({
                    "name": skill,
                    "category": cat,
                    "source_evidence": find_source_evidence(skill, full_text),
                })
            else:
                ambiguous_items.append((skill, hint))

        if ambiguous_items:
            categorized_map: Dict[str, str] = {}
            for i in range(0, len(ambiguous_items), 30):
                batch = ambiguous_items[i:i + 30]
                if hasattr(self.ollama_provider, "categorize_skills_batch"):
                    try:
                        batch_res = await self.ollama_provider.categorize_skills_batch(
                            batch, FIXED_SKILL_CATEGORIES
                        )
                        categorized_map.update(batch_res)
                    except Exception as exc:
                        logger.warning(f"[{correlation_id or 'pipeline'}] Ambiguous skills categorization error: {exc}")

            for skill, _ in ambiguous_items:
                cat = categorized_map.get(skill) or categorized_map.get(skill.lower())
                if not cat or cat not in valid_cats_set:
                    cat = "Uncategorized"
                results.append({
                    "name": skill,
                    "category": cat,
                    "source_evidence": find_source_evidence(skill, full_text),
                })

        return results

    async def extract_and_categorize(
        self, full_text: str, correlation_id: Optional[str] = None
    ) -> List[Dict[str, Optional[str]]]:
        """Extracts all skills from the entire resume text and categorizes them via Ollama
        with source evidence verification.
        """
        if not full_text or not full_text.strip():
            return []

        chunks = self.split_into_chunks(full_text, max_chars=3500)
        extracted_skills_unique: List[str] = []
        seen_lower = set()

        # Bounded concurrency (concurrency=2) to optimize latency while respecting local hardware
        sem = asyncio.Semaphore(2)

        async def process_chunk(chunk_text: str) -> List[str]:
            async with sem:
                try:
                    return await self.ollama_provider.extract_skills_from_chunk(chunk_text)
                except Exception as exc:
                    logger.warning(f"[{correlation_id or 'pipeline'}] Chunk extraction error: {exc}")
                    return []

        chunk_results = await asyncio.gather(*[process_chunk(c) for c in chunks])

        for raw_skills in chunk_results:
            for s in raw_skills:
                s_clean = s.strip()
                # Ground against full resume text, allowing alias and line normalization
                if s_clean and appears_in_source(s_clean, full_text):
                    if s_clean.lower() not in seen_lower:
                        seen_lower.add(s_clean.lower())
                        extracted_skills_unique.append(s_clean)

        if not extracted_skills_unique:
            return []

        # Find label line hints from resume text
        label_hints = self.extract_label_hints(full_text)
        skills_with_hints: List[tuple[str, Optional[str]]] = []
        for s in extracted_skills_unique:
            hint = self.match_hint_for_skill(s, label_hints)
            skills_with_hints.append((s, hint))

        # Categorize skills in batches of 30
        results: List[Dict[str, Optional[str]]] = []
        valid_cats_set = set(FIXED_SKILL_CATEGORIES)

        for i in range(0, len(skills_with_hints), 30):
            batch = skills_with_hints[i:i + 30]
            try:
                categorized_map = await self.ollama_provider.categorize_skills_batch(
                    batch, FIXED_SKILL_CATEGORIES
                )
            except Exception as exc:
                logger.warning(f"[{correlation_id or 'pipeline'}] Categorization batch error: {exc}")
                categorized_map = {}

            for skill, _ in batch:
                cat = categorized_map.get(skill) or categorized_map.get(skill.lower())
                if not cat or cat not in valid_cats_set:
                    cat = "Uncategorized"

                # Locate exact source evidence snippet from resume
                evidence_snippet = find_source_evidence(skill, full_text)

                results.append({
                    "name": skill,
                    "category": cat,
                    "source_evidence": evidence_snippet,
                })

        return results


skill_pipeline = SkillPipeline()
