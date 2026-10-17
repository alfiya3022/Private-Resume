# PrivateResume - Current Project State

## Project phase
Epic 6 - Tailored Resume + Human Editing Complete. Ready for Epic 7 - LaTeX + PDF Generation.

## Current status
- Git repository and foundation verified (Epic 0).
- User authentication, JWT tokens, and user isolation verified (Epic 1).
- Candidate master profile & PyMuPDF resume ingestion verified (Epic 2).
- Job management & Workspace Stage 1 intake engine verified (Epic 3).
- Local-first JD Analysis & requirements extraction engine verified (Epic 4).
- Resume-to-Job Matching & Evidence alignment engine verified (Epic 5).
- Tailored Resume Generation, Versioning & Human Editing verified (Epic 6):
  - SQLAlchemy model `TailoredResume` with relational versioning (`version_number`, `parent_version_id`, `status` ['draft', 'final'], `target_role`, and structured `content` JSON).
  - Historical immutability strictly enforced: editing a finalized resume or explicitly requesting a new version creates an immutable new version row (`v1` -> `v2` -> `v3`). Previous drafts remain frozen.
  - Evidence-grounded `TailoringService`: builds tailored resume drafts directly from genuine candidate profile evidence aligned with JD requirements while strictly excluding missing skills (zero hallucination).
  - Local-first "Ask AI" section refinement: localized section rewrite prompts via `OllamaProvider` (with deterministic fallback) ensuring factual grounding in verified profile skills.
  - REST endpoints operational:
    - `POST /api/v1/jobs/{job_id}/tailor` (201 Created)
    - `GET /api/v1/jobs/{job_id}/tailored-resumes` (200 OK)
    - `GET /api/v1/tailored-resumes/{id}` (200 OK)
    - `PUT /api/v1/tailored-resumes/{id}` (200 OK; in-place draft save or version branching)
    - `POST /api/v1/tailored-resumes/{id}/edit` (200 OK; localized Ask AI section revision)
    - `POST /api/v1/tailored-resumes/{id}/finalize` (200 OK; locks version as FINAL)
  - Alembic migration `006_create_tailoring_tables.py` created.
  - 37 total automated Pytest tests passing (100% pass rate across all modules including unit, version immutability, Ask AI, and security isolation).
  - React Workspace Stage 4 integrated:
    - Version dropdown switcher (`v1 (DRAFT)`, `v2 (FINAL)`), status badges.
    - Section-by-section editors (Headline, Professional Summary, Grouped Technical Skills, Work Experience with bullet editors, Key Projects, Education, Certifications).
    - Interactive "Ask AI" consultation modal with preset prompt directives, custom prompt input, proposed revision box, and "Accept & Apply" workflow.
    - Anti-fabrication integrity callouts and seamless progression to Stage 5.
  - Both QA test workbooks updated with actual execution records:
    - `docs/PrivateResume_Automation_Test_Cases.xlsx` (39 automated tests logged across all modules)
    - `docs/PrivateResume_Manual_Test_Cases.xlsx` (17 manual tests logged across all modules)

## Current next step
Epic 7 - LaTeX + PDF Generation.
Tasks:
1. Template storage and package handling (upload custom ZIP package or use default ATS LaTeX template).
2. Content injection engine: safely escape LaTeX special characters (`&`, `%`, `$`, `#`, `_`, `{`, `}`) and render structured tailored resume content into `.tex` files.
3. Local LaTeX compiler runner invoking `pdflatex` within isolated scratch working directories.
4. Endpoints:
   - `POST /api/v1/tailored-resumes/{id}/generate-pdf`
   - `GET /api/v1/tailored-resumes/{id}/artifacts`
   - `GET /api/v1/tailored-resumes/{id}/preview` (PDF streaming/download)
5. Frontend Stage 5 PDF previewer with download action and status feedback.

## Locked top-level product areas
1. Auth
2. Profile
3. Workspace
4. Applications

## Locked architecture
Modular monolith with React + FastAPI + PostgreSQL, plus local Ollama, local file storage, and local LaTeX during V1 development.

## Locked design
Cream/off-white editorial/modern neo-brutalist SaaS visual direction inspired by the supplied reference image, adapted rather than copied. Workspace is a progressive workflow, not a giant vertically stacked page.

## Locked stack
React, Vite, JavaScript, Tailwind CSS, Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Alembic, Ollama, PyMuPDF, LaTeX, Pytest, Playwright, Postman, Git/GitHub, Docker/Docker Compose, GitHub Actions.

## Runtime placement
- React: Docker application environment; local Vite development is allowed for fast iteration
- FastAPI: Docker
- PostgreSQL: Docker with persistent volume
- Ollama: local/native
- LaTeX: included in the backend Docker image

## QA test management
- Manual and automation testing are maintained in separate module-wise Excel workbooks.
- Test cases are added and execution results are logged after the relevant feature reaches its testing stage.
- CI checks and merge must pass before the project advances to the next feature.

## Known TBD items
- Exact Ollama model benchmark for JD analysis and tailoring
- Deployment target (intentionally TBD for V1 local-first product)

## Known non-goals
No autonomous job applications, no fabricated qualifications, no recruiter portal, no candidate ranking, no V1 job-board integrations, no unnecessary infrastructure additions.

## Current issues
None. Epics 0, 1, 2, 3, 4, and 5 verified and passing.
