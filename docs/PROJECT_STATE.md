# PrivateResume - Current Project State

## Project phase
Epic 4 - JD Analysis Complete. Ready for Epic 5 - Resume-to-Job Matching.

## Current status
- Git repository and foundation verified (Epic 0).
- User authentication, JWT tokens, and user isolation verified (Epic 1).
- Candidate master profile & PyMuPDF resume ingestion verified (Epic 2).
- Job management & Workspace Stage 1 intake engine verified (Epic 3).
- Local-first JD Analysis & requirements extraction engine verified (Epic 4):
  - AI provider abstraction `OllamaProvider` communicating with local host Ollama instance (`http://localhost:11434`) via JSON-mode structured prompting.
  - Robust deterministic extraction fallback parser mapping JD requirements to industry taxonomy (languages, frameworks, databases, tools, cloud, soft skills, responsibilities, qualifications, and experience level).
  - SQLAlchemy relational model `JobRequirement` storing structured requirements with foreign key to `Job.id`.
  - Service layer `AnalysisService` implementing job requirement extraction, upsertion, and multi-tenant isolation.
  - REST endpoints operational under `/api/v1/jobs`:
    - `POST /jobs/{job_id}/analyze` (200 OK returning `JobAnalysisResponse`)
    - `GET /jobs/{job_id}/analysis` (200 OK; 404 on missing or unauthorized access)
  - Alembic migration `004_create_analysis_tables.py` created.
  - 31 total automated Pytest tests passing (100% pass rate across unit, API contracts, negative scenarios, and security isolation tests).
  - React Workspace Stage 2 integrated: displays categorized required vs preferred technical skills, categorized tech stack breakdown, key responsibilities, minimum qualifications, re-analyze trigger, and transition to Stage 3.
  - Both QA test workbooks updated with actual execution records:
    - `docs/PrivateResume_Automation_Test_Cases.xlsx` (`Auth`, `Master_Resume`, `Profile_Personal`, `Workspace_Job_Input`, `JD_Analysis`: 29 automated tests logged)
    - `docs/PrivateResume_Manual_Test_Cases.xlsx` (`Auth`, `Master_Resume`, `Workspace_Job_Input`, `JD_Analysis`: 9 manual tests logged)

## Current next step
Epic 5 - Resume-to-Job Matching.
Tasks:
1. Evidence matching engine (`app/services/matching_service.py`) executing primarily deterministic rules after structured extraction.
2. Evidence classification into four mandatory categories:
   - Matched skills
   - Weakly represented skills
   - Missing skills
   - Unsupported claims (flagged to prevent fabrication)
3. Calculation of "Estimated Job Match" metric (strictly not labeled an ATS score).
4. Relational `MatchAnalysis` entity and migration `005_create_match_tables.py`.
5. Endpoint: `POST /api/v1/jobs/{job_id}/match`.
6. Frontend Stage 3 Match Analysis & Evidence drawer UI.

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
None. Epics 0, 1, 2, 3, and 4 verified and passing.
