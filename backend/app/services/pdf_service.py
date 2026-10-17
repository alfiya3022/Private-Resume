import re
from typing import Dict, List, Tuple
import fitz  # PyMuPDF


class PdfService:
    # Common section header patterns
    SECTION_PATTERNS = {
        "summary": r"^(?:professional\s+)?(?:summary|profile|about\s+me|objective)",
        "skills": r"^(?:technical\s+)?(?:skills|competencies|technologies|tools|expertise)",
        "experience": r"^(?:work\s+)?(?:experience|employment|work\s+history|professional\s+experience)",
        "projects": r"^(?:key\s+)?(?:projects|personal\s+projects|academic\s+projects)",
        "education": r"^(?:education|academic\s+background|qualifications)",
        "certifications": r"^(?:certifications|licenses|courses|awards)",
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

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extracts plain text from a PDF file using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            full_text = []
            for page in doc:
                text = page.get_text("text")
                if text:
                    full_text.append(text)
            doc.close()
            return "\n\n".join(full_text).strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

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
            if len(line.split()) <= 4:
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
            # Word boundary search
            pattern = rf"\b{re.escape(skill_key)}\b"
            if re.search(pattern, text_lower):
                found_skills.append(canonical_name)
        return sorted(list(set(found_skills)))



pdf_service = PdfService()
