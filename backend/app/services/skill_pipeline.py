import re
from typing import List, Dict, Optional, Any
from app.services.ai.resume_llm_schemas import LLMChunkSkills, LLMSkillCategoryBatch

FIXED_SKILL_CATEGORIES: List[str] = [
    "Programming Language",
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
    "Other",
]

LABEL_LINE_PATTERN = re.compile(
    r"^\s*(?:-\s*)?([A-Za-z][A-Za-z &/+.\-]{2,40}?)\s*:\s*(\S.*)$",
    re.MULTILINE,
)


def appears_in_source(value: Optional[str], source: Optional[str]) -> bool:
    """Checks whether an alphanumeric representation of value is contained in source."""
    if not value or not source:
        return False
    clean_val = re.sub(r"[^a-zA-Z0-9]", "", str(value)).lower()
    clean_src = re.sub(r"[^a-zA-Z0-9]", "", str(source)).lower()
    if not clean_val:
        return False
    return clean_val in clean_src


class SkillPipeline:
    def __init__(self, ollama_provider=None):
        from app.services.ai.ollama_provider import ollama_provider as default_provider
        self.ollama_provider = ollama_provider or default_provider

    def split_into_chunks(self, text: str, max_chars: int = 1500) -> List[str]:
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
            if clean_skill in clean_content:
                return label
        return None

    async def extract_and_categorize(self, full_text: str) -> List[Dict[str, Optional[str]]]:
        """Extracts all skills from the entire resume text and categorizes them via Ollama."""
        if not full_text or not full_text.strip():
            return []

        chunks = self.split_into_chunks(full_text)
        extracted_skills_unique: List[str] = []
        seen_lower = set()

        for chunk in chunks:
            try:
                chunk_skills = await self.ollama_provider.extract_skills_from_chunk(chunk)
                for s in chunk_skills:
                    s_clean = s.strip()
                    if s_clean and appears_in_source(s_clean, chunk):
                        if s_clean.lower() not in seen_lower:
                            seen_lower.add(s_clean.lower())
                            extracted_skills_unique.append(s_clean)
            except Exception:
                continue

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
                categorized_map = await self.ollama_provider.categorize_skills_batch(batch, FIXED_SKILL_CATEGORIES)
            except Exception:
                categorized_map = {}

            for skill, _ in batch:
                cat = categorized_map.get(skill) or categorized_map.get(skill.lower())
                if not cat or cat not in valid_cats_set:
                    cat = "Other"
                results.append({"name": skill, "category": cat})

        return results


skill_pipeline = SkillPipeline()
