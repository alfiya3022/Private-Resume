import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.pdf_service import pdf_service, _appears_in_source
from app.services.skill_pipeline import SkillPipeline, FIXED_SKILL_CATEGORIES
from app.services.ai.resume_llm_schemas import (
    LLMResumeExtraction,
    LLMPersonalInfo,
    LLMEducationItem,
    LLMExperienceItem,
    LLMProjectItem,
    LLMCertificationItem,
)


@pytest.mark.asyncio
async def test_llm_first_parsing_non_standard_headings_and_project_boundaries():
    """1. Resume with non-standard headings and consecutive projects:
    Asserts sections land correctly, 2 separate projects, bullets not merged.
    """
    resume_text = """Jane Doe
jane.doe@example.com
+1 555-0199

Technical Experience
Tech Corp
Software Engineer
Jan 2022 - Present
- Built backend APIs with high throughput.

Academic Projects
Portfolio Website
React, CSS
- Designed responsive layout.
- Deployed on Vercel with automated CI.

Built Resume Parser
Python, FastAPI
- Parsed PDF resumes without templates.

Education Credentials
State University
Bachelor of Science in Computer Science
2018 - 2022
"""

    fake_extraction = LLMResumeExtraction(
        personal_info=LLMPersonalInfo(
            name="Jane Doe",
            email="jane.doe@example.com",
            phone="+1 555-0199",
            location="",
        ),
        summary="",
        education=[
            LLMEducationItem(
                institution="State University",
                degree="Bachelor of Science in Computer Science",
                start_date="2018",
                end_date="2022",
            )
        ],
        experience=[
            LLMExperienceItem(
                company="Tech Corp",
                title="Software Engineer",
                start_date="Jan 2022",
                end_date="Present",
                is_current=True,
                bullets=["Built backend APIs with high throughput."],
            )
        ],
        projects=[
            LLMProjectItem(
                title="Portfolio Website",
                technologies=["React", "CSS"],
                bullets=[
                    "Designed responsive layout.",
                    "Deployed on Vercel with automated CI.",
                ],
            ),
            LLMProjectItem(
                title="Built Resume Parser",
                technologies=["Python", "FastAPI"],
                bullets=["Parsed PDF resumes without templates."],
            ),
        ],
        certifications=[],
    )

    with patch("app.services.ai.ollama_provider.ollama_provider.is_available", new_callable=AsyncMock) as mock_avail, \
         patch("app.services.ai.ollama_provider.ollama_provider.extract_full_resume_structure", new_callable=AsyncMock) as mock_struct, \
         patch("app.services.pdf_service.skill_pipeline.extract_and_categorize", new_callable=AsyncMock) as mock_skills, \
         patch.object(pdf_service, "extract_links_from_pdf", return_value=[]):
        
        mock_avail.return_value = True
        mock_struct.return_value = fake_extraction
        mock_skills.return_value = [{"name": "React", "category": "Frontend Framework"}, {"name": "Python", "category": "Programming Language"}]

        result = await pdf_service.extract_full_resume_data_hybrid(
            file_path="dummy.pdf",
            raw_text=resume_text,
            plain_text=resume_text,
        )

        # Assert correct placement and 2 separate projects
        assert len(result["projects"]) == 2
        p0 = result["projects"][0]
        p1 = result["projects"][1]

        assert p0["title"] == "Portfolio Website"
        assert p0["bullets"] == [
            "Designed responsive layout.",
            "Deployed on Vercel with automated CI.",
        ]
        assert p0["technologies"] == ["React", "CSS"]

        assert p1["title"] == "Built Resume Parser"
        assert p1["bullets"] == ["Parsed PDF resumes without templates."]
        assert p1["technologies"] == ["Python", "FastAPI"]

        # Bullets were not merged between projects
        assert len(p0["bullets"]) == 2
        assert len(p1["bullets"]) == 1
        assert "Parsed PDF resumes without templates." not in p0["bullets"]

        # Experience verified
        assert len(result["experience"]) == 1
        assert result["experience"][0]["company"] == "Tech Corp"


@pytest.mark.asyncio
async def test_grounding_drops_hallucinated_bullet_and_skill():
    """2. A hallucinated bullet and a hallucinated skill returned by LLM are dropped by grounding."""
    resume_text = """Alex Smith
alex.smith@example.com
Acme Labs
Senior Developer
- Implemented real-time telemetry streaming.
Skills: Python, Redis
"""

    fake_extraction = LLMResumeExtraction(
        personal_info=LLMPersonalInfo(name="Alex Smith", email="alex.smith@example.com"),
        experience=[
            LLMExperienceItem(
                company="Acme Labs",
                title="Senior Developer",
                bullets=[
                    "Implemented real-time telemetry streaming.",
                    "Invented teleportation device in top secret basement.",  # Hallucinated
                ],
            )
        ],
    )

    fake_provider = MagicMock()
    fake_provider.extract_skills_from_chunk = AsyncMock(
        return_value=["Python", "Redis", "Telepathic Debugging"]  # "Telepathic Debugging" hallucinated
    )
    fake_provider.categorize_skills_batch = AsyncMock(
        return_value={"Python": "Programming Language", "Redis": "Database"}
    )

    pipeline = SkillPipeline(ollama_provider=fake_provider)

    with patch("app.services.ai.ollama_provider.ollama_provider.is_available", new_callable=AsyncMock) as mock_avail, \
         patch("app.services.ai.ollama_provider.ollama_provider.extract_full_resume_structure", new_callable=AsyncMock) as mock_struct, \
         patch("app.services.pdf_service.skill_pipeline", pipeline), \
         patch.object(pdf_service, "extract_links_from_pdf", return_value=[]):

        mock_avail.return_value = True
        mock_struct.return_value = fake_extraction

        result = await pdf_service.extract_full_resume_data_hybrid(
            file_path="dummy.pdf",
            raw_text=resume_text,
            plain_text=resume_text,
        )

        # Experience grounding: hallucinated bullet dropped
        exp = result["experience"][0]
        assert "Implemented real-time telemetry streaming." in exp["bullets"]
        assert "Invented teleportation device in top secret basement." not in exp["bullets"]
        assert len(exp["bullets"]) == 1

        # Skill grounding: hallucinated skill dropped
        skill_names = [s["name"] for s in result["skills"]]
        assert "Python" in skill_names
        assert "Redis" in skill_names
        assert "Telepathic Debugging" not in skill_names


@pytest.mark.asyncio
async def test_skills_from_all_sections_and_categorization_with_hints():
    """3. Skills come from skills list, project tech line, and bullet;
    categories validated against fixed list (invalid -> 'Other'), and label hints passed.
    """
    resume_text = """Candidate Name
candidate@example.com
Backend: Python, PostgreSQL
Projects:
Task Manager
Technologies: React
- Orchestrated deployment using Docker containers.
"""

    fake_provider = MagicMock()
    # Skills found across skills list (Python, PostgreSQL), tech line (React), and bullet (Docker)
    fake_provider.extract_skills_from_chunk = AsyncMock(
        return_value=["Python", "PostgreSQL", "React", "Docker"]
    )

    captured_batches = []

    async def mock_categorize(batch, categories):
        captured_batches.append(batch)
        # Return valid category for Python, invalid category for React, valid for PostgreSQL, omitted for Docker
        return {
            "Python": "Programming Language",
            "PostgreSQL": "Database",
            "React": "Invalid Category Example",  # Not in fixed list
            # Docker omitted to verify fallback to Other
        }

    fake_provider.categorize_skills_batch = AsyncMock(side_effect=mock_categorize)

    pipeline = SkillPipeline(ollama_provider=fake_provider)
    skills = await pipeline.extract_and_categorize(resume_text)

    # Verify hint reached the batch for skills under "Backend:" label line
    assert len(captured_batches) > 0
    batch_entries = captured_batches[0]
    skill_hint_map = {item[0]: item[1] for item in batch_entries}

    assert skill_hint_map.get("Python") == "Backend"
    assert skill_hint_map.get("PostgreSQL") == "Backend"
    assert skill_hint_map.get("React") == "Technologies"
    assert skill_hint_map.get("Docker") is None

    # Verify categorization results
    category_map = {s["name"]: s["category"] for s in skills}
    assert category_map["Python"] == "Programming Language"
    assert category_map["PostgreSQL"] == "Database"
    assert category_map["React"] == "Other"  # Invalid category normalized to Other
    assert category_map["Docker"] == "Other"  # Missing category normalized to Other

    for s in skills:
        assert s["category"] in FIXED_SKILL_CATEGORIES


@pytest.mark.asyncio
async def test_llm_failure_triggers_regex_fallback():
    """4. The fake LLM raises an error: regex fallback still returns non-empty sections and skills."""
    plain_text = """John Doe
john.doe@example.com
Phone: +1 555 123 4567
LinkedIn: https://linkedin.com/in/johndoe
GitHub: https://github.com/johndoe

SUMMARY
Experienced software engineer with strong technical skills.

SKILLS
Python, JavaScript, React, Docker

EXPERIENCE
Software Engineer
Acme Corp
2021 - Present
- Developed scalable cloud microservices.

PROJECTS
OpenSource Tool
Technologies: Python, FastAPI
- Built CLI automation.

EDUCATION
Bachelor of Science in Computer Science
MIT
2017 - 2021

CERTIFICATIONS
AWS Certified Developer
Amazon Web Services - 2022
"""

    with patch("app.services.ai.ollama_provider.ollama_provider.is_available", new_callable=AsyncMock) as mock_avail, \
         patch("app.services.ai.ollama_provider.ollama_provider.extract_full_resume_structure", new_callable=AsyncMock) as mock_struct, \
         patch("app.services.pdf_service.skill_pipeline.extract_and_categorize", new_callable=AsyncMock) as mock_skills, \
         patch.object(pdf_service, "extract_links_from_pdf", return_value=[]):

        mock_avail.return_value = True
        mock_struct.side_effect = RuntimeError("Ollama connection failed")
        mock_skills.side_effect = RuntimeError("Skill pipeline failed")

        result = await pdf_service.extract_full_resume_data_hybrid(
            file_path="dummy.pdf",
            raw_text=plain_text,
            plain_text=plain_text,
        )

        assert result is not None
        assert result["personal_info"]["name"] == "John Doe"
        assert result["personal_info"]["email"] == "john.doe@example.com"
        assert len(result["experience"]) >= 1
        assert result["experience"][0]["company"] == "Acme Corp"
        assert len(result["projects"]) >= 1
        assert "OpenSource Tool" in result["projects"][0]["title"]
        assert len(result["education"]) >= 1
        assert len(result["skills"]) >= 1


def test_extract_text_from_pdf_picks_plain_when_markdown_has_fewer_sections():
    """5. extract_text_from_pdf picks plain text when markdown text has fewer detected sections."""
    plain_text = """Jane Doe
SUMMARY
Software developer with full stack expertise.

SKILLS
Python, JavaScript, React

EXPERIENCE
Developer at Beta Corp
2020 - 2023
- Built web apps.

PROJECTS
Project A
- Project description.

EDUCATION
BS in Computer Science
Tech University
"""

    # Markdown misses sections (e.g. collapsed or bad headers)
    markdown_text = """Jane Doe
SUMMARY
Software developer with full stack expertise.

EXPERIENCE
Developer at Beta Corp
- Built web apps.
"""

    with patch.object(pdf_service, "_extract_plain", return_value=plain_text), \
         patch.object(pdf_service, "_extract_markdown", return_value=markdown_text):

        selected_text = pdf_service.extract_text_from_pdf("dummy.pdf")
        assert selected_text == plain_text


@pytest.mark.asyncio
async def test_non_technical_skill_categories_and_fallback():
    """6. Finance, HR, and business skills receive dedicated non-technical categories, and unknown categories fallback to 'Other'."""
    resume_text = """Anita Sharma
anita.sharma@example.com
Finance & HR Specialist
Skills: Tally, Financial Reporting, Payroll, Talent Acquisition, Quantum Teleportation
"""
    fake_provider = MagicMock()
    fake_provider.extract_skills_from_chunk = AsyncMock(
        return_value=["Tally", "Financial Reporting", "Payroll", "Talent Acquisition", "Quantum Teleportation"]
    )

    async def mock_categorize(batch, categories):
        return {
            "Tally": "Finance & Accounting",
            "Financial Reporting": "Finance & Accounting",
            "Payroll": "HR & Recruitment",
            "Talent Acquisition": "HR & Recruitment",
            "Quantum Teleportation": "SciFi Fiction",
        }

    fake_provider.categorize_skills_batch = AsyncMock(side_effect=mock_categorize)

    pipeline = SkillPipeline(ollama_provider=fake_provider)
    skills = await pipeline.extract_and_categorize(resume_text)

    cat_map = {s["name"]: s["category"] for s in skills}
    assert cat_map["Tally"] == "Finance & Accounting"
    assert cat_map["Financial Reporting"] == "Finance & Accounting"
    assert cat_map["Payroll"] == "HR & Recruitment"
    assert cat_map["Talent Acquisition"] == "HR & Recruitment"
    assert cat_map["Quantum Teleportation"] == "Other"

    for s in skills:
        assert s["category"] in FIXED_SKILL_CATEGORIES

