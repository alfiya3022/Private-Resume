# PrivateResume - Current Project State

## Project phase
Epic 3 - Job Management Complete. Ready for Epic 4 - JD Analysis.

## Current status
- Git repository and foundation verified (Epic 0).
- User authentication, JWT tokens, and user isolation verified (Epic 1).
- Candidate master profile & PyMuPDF resume ingestion verified (Epic 2).
- Job management & Workspace Stage 1 intake engine verified (Epic 3):
  - SQLAlchemy relational model for `Job` (`id`, `user_id`, `company`, `title`, `location`, `job_url`, `salary`, `raw_jd_text`, `status`, timestamps).
  - Pydantic models for job creation, update, and response with non-empty string validation.
  - Service layer `JobService` implementing job persistence, queries, updates, and cascading user isolation.
  - REST endpoints operational under `/api/v1/jobs`:
    - `POST /jobs` (201 Created)
    - `GET /jobs` (200 OK with optional status filter)
    - `GET /jobs/{id}` (200 OK; 404 for nonexistent or unauthorized access)
    - `PUT /jobs/{id}` (200 OK; 404 for unauthorized access)
    - `DELETE /jobs/{id}` (204 No Content; 404 for unauthorized access)
  - Alembic migration `003_create_jobs_table.py` created.
  - 27 total automated Pytest tests passing (100% pass rate across unit, API contracts, negative validation, and security isolation tests).
  - React Workspace Stage 1 integrated: shows active master resume health, provides target opportunity input form, lists previously saved jobs, and transitions to Stage 2 upon job submission.
  - Both QA test workbooks updated with actual execution records:
    - `docs/PrivateResume_Automation_Test_Cases.xlsx` (`Auth`, `Master_Resume`, `Profile_Personal`, `Workspace_Job_Input`: 25 automated tests logged)
    - `docs/PrivateResume_Manual_Test_Cases.xlsx` (`Auth`, `Master_Resume`, `Workspace_Job_Input`: 7 manual tests logged)

## Current next step
Epic 4 - JD Analysis.
Tasks:
1. Ollama provider abstraction (`app/services/ai/ollama_provider.py`) communicating with local host Ollama instance (`http://localhost:11434`).
2. Structured output validation schemas for required vs preferred skills, frameworks, databases, tools, cloud, responsibilities, and qualifications.
3. Job requirements persistence (`JobRequirement` model and `004_create_analysis_tables.py`).
4. Endpoint: `POST /api/v1/jobs/{job_id}/analyze`.
5. Frontend Stage 2 Job Analysis interactive view.

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
None. Epics 0, 1, 2, and 3 verified and passing.
