import re
import httpx
from typing import Dict, Any, List


class GitHubService:
    @staticmethod
    def parse_repo_info(github_url: str) -> tuple[str, str]:
        """Extract (owner, repo) from GitHub URL."""
        pattern = r"github\.com[/:]([\w\-\.]+)/([\w\-\.]+)"
        match = re.search(pattern, github_url)
        if match:
            owner, repo = match.group(1), match.group(2)
            return owner, repo.removesuffix(".git")
        
        # Fallback if bare user/repo or custom URL
        clean = github_url.strip().strip("/").split("/")
        if len(clean) >= 2:
            return clean[-2], clean[-1].removesuffix(".git")
        return "developer", "project"

    @classmethod
    async def extract_project_from_github(cls, github_url: str) -> Dict[str, Any]:
        """
        Extract project title, description, tech stack, and accomplishment bullets from GitHub repo and README.md.
        Gracefully handles network errors, private repos, or rate limits with intelligent fallbacks.
        """
        owner, repo = cls.parse_repo_info(github_url)
        fallback_title = repo.replace("-", " ").replace("_", " ").title()

        result: Dict[str, Any] = {
            "title": fallback_title,
            "role": "Creator / Maintainer",
            "description": f"Open-source software project hosted on GitHub ({owner}/{repo}).",
            "technologies": [],
            "bullets": [],
            "url": github_url.strip(),
        }

        headers = {
            "User-Agent": "PrivateResume-Local/1.0",
            "Accept": "application/vnd.github.v3+json",
        }

        readme_content = ""
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                # 1. Query GitHub Repo API
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                repo_resp = await client.get(api_url, headers=headers)
                if repo_resp.status_code == 200:
                    data = repo_resp.json()
                    if data.get("name"):
                        result["title"] = data["name"].replace("-", " ").replace("_", " ").title()
                    if data.get("description"):
                        result["description"] = data["description"]
                    if data.get("language"):
                        result["technologies"].append(data["language"])
                    if data.get("topics"):
                        for topic in data["topics"][:6]:
                            fmt = topic.replace("-", " ").title()
                            if fmt not in result["technologies"]:
                                result["technologies"].append(fmt)

                # 2. Fetch README markdown
                raw_branches = ["HEAD", "main", "master", "develop"]
                for branch in raw_branches:
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
                    r_resp = await client.get(raw_url, headers={"User-Agent": "PrivateResume-Local/1.0"})
                    if r_resp.status_code == 200 and r_resp.text.strip():
                        readme_content = r_resp.text
                        break
        except Exception:
            # Fallback will take care of populating sensible data
            pass

        # 3. Parse README markdown for title, tech stack, description, and bullet points
        if readme_content:
            cls._parse_readme(readme_content, result)

        # 4. Ensure we have strong bullet points if none extracted from markdown
        if not result["bullets"]:
            stack_str = ", ".join(result["technologies"][:3]) if result["technologies"] else "modern tooling"
            result["bullets"] = [
                f"Designed and implemented {result['title']} utilizing {stack_str} with modular codebase structure.",
                f"Architected core functionality and published repository documentation at {github_url.strip()}.",
            ]

        return result

    @classmethod
    def _parse_readme(cls, content: str, result: Dict[str, Any]):
        lines = content.splitlines()

        # 1. Extract Title from first H1
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("# ") and len(line_str) > 2:
                raw_title = re.sub(r"[#*`_\[\]]", "", line_str).strip()
                raw_title = re.sub(r"^[\W_]+", "", raw_title).strip()
                if raw_title and len(raw_title) < 60:
                    result["title"] = raw_title
                break

        # 2. Extract Description from introductory paragraph
        desc_lines = []
        found_header = False
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("#"):
                found_header = True
                continue
            if found_header:
                # Skip badge images and HTML
                if line_str.startswith(("[!", "![", "<", ">")):
                    continue
                if line_str and not line_str.startswith(("-", "*", "•")):
                    desc_lines.append(line_str)
                    if len(" ".join(desc_lines)) > 80:
                        break
                elif line_str == "" and desc_lines:
                    break

        if desc_lines and (not result.get("description") or "Open-source software project" in result["description"]):
            cleaned_desc = " ".join(desc_lines)
            # Remove markdown links
            cleaned_desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned_desc)
            cleaned_desc = re.sub(r"[`*]", "", cleaned_desc).strip()
            if len(cleaned_desc) > 20:
                result["description"] = cleaned_desc[:280]

        # 3. Tech Stack Detection
        tech_catalog = [
            "Python", "FastAPI", "React", "TypeScript", "JavaScript", "Docker", "PostgreSQL",
            "MongoDB", "Redis", "Next.js", "Vue", "Angular", "Tailwind CSS", "Node.js", "Express",
            "GraphQL", "Kubernetes", "AWS", "GCP", "Azure", "PyTorch", "TensorFlow", "Flask",
            "Django", "Java", "Spring Boot", "Go", "Golang", "Rust", "C++", "C#", ".NET",
            "MySQL", "SQLite", "SQLAlchemy", "Pydantic", "HTML5", "CSS3", "Linux", "Git",
            "GitHub Actions", "Ollama", "LaTeX"
        ]
        content_lower = content.lower()
        for tech in tech_catalog:
            pattern = rf"\b{re.escape(tech.lower())}\b"
            if re.search(pattern, content_lower) and tech not in result["technologies"]:
                result["technologies"].append(tech)

        result["technologies"] = result["technologies"][:8]

        # 4. Extract bullet accomplishments from markdown lists
        bullets = []
        for line in lines:
            line_str = line.strip()
            if line_str.startswith(("- ", "* ", "• ")) and len(line_str) > 20:
                bullet = re.sub(r"^[-*•]\s*", "", line_str).strip()
                bullet = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", bullet)
                bullet = re.sub(r"[`*]", "", bullet)
                if len(bullet) > 20 and not bullet.startswith("http"):
                    bullets.append(bullet)
                    if len(bullets) >= 4:
                        break

        if bullets:
            result["bullets"] = bullets


github_service = GitHubService()
