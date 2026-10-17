# PrivateResume - Current Project State

## Project phase
Epic 2 - Profile + Master Resume Complete. Ready for Epic 3 - Job Management.

## Current status
- Git repository and foundation verified (Epic 0).
- User authentication, JWT tokens, and user isolation verified (Epic 1).
- Candidate master profile & resume ingestion engine verified (Epic 2):
  - SQLAlchemy relational models for `CandidateProfile`, `CandidateSkill`, `Project`, `Experience`, `Education`, `Certification`, and `MasterResume`.
  - Local storage service with path traversal protection, user directory isolation, and upload file size limits.
  - PyMuPDF (`fitz`) text extraction pipeline with section segmentation and canonical skill detection.
  - Master resume upload flow (`POST /api/v1/resumes`) auto-extracts text and populates candidate profile skills.
  - Profile CRUD and sub-item endpoints (`/api/v1/profile`, `/skills`, `/projects`, `/experiences`, `/educations`, `/certifications`).
  - Alembic migration `002_create_profile_tables.py` created.
  - 22 total automated Pytest tests passing (100% pass rate across unit, API, negative, and security isolation tests).
  - React Profile Workspace updated with PDF upload drag-and-drop, live parsing feedback, and tabbed evidence editing.
  - Both QA test workbooks updated with actual execution records:
    - `docs/PrivateResume_Automation_Test_Cases.xlsx` (`Auth`, `Master_Resume`, `Profile_Personal`: 20 automated tests logged)
    - `docs/PrivateResume_Manual_Test_Cases.xlsx` (`Auth`, `Master_Resume`: 5 manual tests logged)

## Current next step
Epic 3 - Job Management.
Tasks:
1. Job entity & relational model (`Job` with company, title, location, salary, raw job description text, status).
2. Job CRUD endpoints (`POST /api/v1/jobs`, `GET /api/v1/jobs`, `GET /api/v1/jobs/{id}`, `PUT /api/v1/jobs/{id}`, `DELETE /api/v1/jobs/{id}`).
3. Workspace Stage 1 integration with Job creation and master resume linkage.
4. Pytest suite for Job management, validation, and multi-tenant isolation.

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
None. Epics 0, 1, and 2 verified and passing.
