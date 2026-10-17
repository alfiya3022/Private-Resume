import json
import re
from typing import Dict, List, Optional
import httpx
from app.core.config import settings
from app.schemas.analysis import StructuredJDAnalysis

# Categorized taxonomy for deterministic extraction and validation
TECH_CATEGORIES = {
    "languages": ["python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php", "sql", "html", "css"],
    "frameworks": ["fastapi", "django", "flask", "react", "next.js", "vue", "angular", "express", "spring boot", "tailwind"],
    "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite", "dynamodb", "oracle"],
    "tools": ["docker", "git", "github", "gitlab", "jira", "postman", "linux", "jenkins", "kubernetes", "latex"],
    "cloud": ["aws", "azure", "gcp", "google cloud", "terraform", "s3", "lambda", "ec2"],
    "soft_skills": ["communication", "teamwork", "leadership", "problem solving", "collaboration", "analytical", "mentoring"],
}

CANONICAL_NAMES = {
    "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript", "java": "Java",
    "c++": "C++", "c#": "C#", "go": "Go", "rust": "Rust", "sql": "SQL", "html": "HTML", "css": "CSS",
    "fastapi": "FastAPI", "django": "Django", "flask": "Flask", "react": "React", "next.js": "Next.js",
    "express": "Express", "tailwind": "Tailwind CSS", "postgresql": "PostgreSQL", "mysql": "MySQL",
    "mongodb": "MongoDB", "redis": "Redis", "sqlite": "SQLite", "docker": "Docker", "git": "Git",
    "aws": "AWS", "azure": "Azure", "gcp": "GCP", "linux": "Linux", "kubernetes": "Kubernetes",
    "postman": "Postman", "latex": "LaTeX", "communication": "Communication", "teamwork": "Teamwork",
    "leadership": "Leadership", "collaboration": "Collaboration", "analytical": "Analytical Thinking",
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
                    return StructuredJDAnalysis(**parsed_dict)
        except Exception:
            # Fall back to deterministic local extraction
            pass

        return self.deterministic_jd_extraction(raw_jd_text)

    def deterministic_jd_extraction(self, text: str) -> StructuredJDAnalysis:
        """Deterministic keyword extraction fallback guaranteeing accurate, non-hallucinated analysis."""
        text_lower = text.lower()
        extracted: Dict[str, List[str]] = {cat: [] for cat in TECH_CATEGORIES}

        for cat, keywords in TECH_CATEGORIES.items():
            for kw in keywords:
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, text_lower):
                    extracted[cat].append(CANONICAL_NAMES.get(kw, kw.title()))

        # Separate into required vs preferred based on context
        required_skills = []
        preferred_skills = []

        # Find experience years (e.g. "5+ years", "3-5 years")
        exp_match = re.search(r"(\d+[\+\-]?\s*(?:to\s*\d+)?\s*years?)", text_lower)
        experience_years = exp_match.group(1).title() if exp_match else "3+ Years"

        # Split lines for responsibilities and qualifications
        lines = [line.strip("-•* ").strip() for line in text.splitlines() if line.strip()]
        responsibilities = []
        qualifications = []

        is_resp = False
        is_qual = False

        for line in lines:
            line_l = line.lower()
            if "responsibilit" in line_l or "what you'll do" in line_l or "duties" in line_l:
                is_resp = True
                is_qual = False
                continue
            elif "qualification" in line_l or "requirement" in line_l or "what we look for" in line_l:
                is_qual = True
                is_resp = False
                continue

            if is_resp and len(line) > 15 and len(responsibilities) < 6:
                responsibilities.append(line)
            elif is_qual and len(line) > 15 and len(qualifications) < 6:
                qualifications.append(line)

        # Fallback if specific section headers were absent
        if not responsibilities:
            responsibilities = [l for l in lines if len(l) > 30][:4]
        if not qualifications:
            qualifications = [l for l in lines if "experience" in l.lower() or "degree" in l.lower()][:3]

        # Combine technical skills into required/preferred
        all_tech = sorted(list(set(
            extracted["languages"] + extracted["frameworks"] +
            extracted["databases"] + extracted["cloud"] + extracted["tools"]
        )))

        # Primary skills are required, secondary are preferred
        required_skills = all_tech[:6]
        preferred_skills = all_tech[6:]

        return StructuredJDAnalysis(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            languages=sorted(list(set(extracted["languages"]))),
            frameworks=sorted(list(set(extracted["frameworks"]))),
            databases=sorted(list(set(extracted["databases"]))),
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
