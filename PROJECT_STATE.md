# PrivateResume - Current Project State

## Project phase
Epic 8 - Resume Validation Engine Complete. Ready for Epic 9 - Application Tracking.

## Current status
- Git repository and foundation verified (Epic 0).
- User authentication, JWT tokens, and user isolation verified (Epic 1).
- Candidate master profile & PyMuPDF resume ingestion verified (Epic 2).
- Job management & Workspace Stage 1 intake engine verified (Epic 3).
- Local-first JD Analysis & requirements extraction engine verified (Epic 4).
- Resume-to-Job Matching & Evidence alignment engine verified (Epic 5).
- Tailored Resume Generation, Versioning & Human Editing verified (Epic 6).
- LaTeX + PDF Generation & Document Streaming verified (Epic 7).
- Resume Validation Engine verified (Epic 8):
  - ATS pre-flight engine (`ValidationService`) evaluating 6 objective checks:
    1. PDF Document Health (valid page count, structure, size)
    2. Machine-Readable Text Extractability via PyMuPDF
    3. Contact Details Detection (Email, Phone, Name in header)
    4. Standard ATS Headings (Summary, Experience, Skills, Education)
    5. Template Placeholder Audit (identifies unresolved tokens `TODO`, `[Company]`, `[Title]`, `Lorem ipsum`, `TBD`)
    6. Candidate Evidence Integrity (verifies skill claims strictly match master candidate profile)
  - Objective scoring algorithm yielding PASS (100%), WARN (85%), or FAIL (60%) with granular check diagnostics.
  - Relational `ResumeValidation` model registered in Alembic migration `008_create_validation_tables.py` and applied.
  - REST endpoints operational under `/api/v1/tailored-resumes`:
    - `POST /{resume_id}/validate`: Runs pre-flight audit and persists validation record.
    - `GET /{resume_id}/validation`: Retrieves existing validation report.
  - Pytest validation test suite passing (`backend/tests/test_validation.py`):
    - Uncompiled PDF rejection guard (400 Bad Request)
    - Full 6-check audit execution and report retrieval
    - Multi-tenant user isolation enforcement
  - Workspace Stage 5 UI integrated:
    - Minimal, sleek "ATS Pre-Flight Quality Gate" card with score pill and status badges.
    - Interactive 6-check grid with Pass/Warn/Fail indicators and resolution hints.
    - Automatic validation on PDF compilation with on-demand "Re-Run ATS Audit" capability.
  - Both QA test workbooks updated with actual execution records:
    - `docs/PrivateResume_Automation_Test_Cases.xlsx` (46 automated tests logged across all modules)
    - `docs/PrivateResume_Manual_Test_Cases.xlsx` (21 manual tests logged across all modules)

## Current next step
Epic 9 - Application Tracking.
Tasks:
1. Application model and schema linking target job, tailored resume version, status history, notes, and application dates.
2. Application tracking service and endpoints:
   - `GET /api/v1/applications`: List tracked applications with status filters.
   - `POST /api/v1/applications`: Log application from Workspace Stage 5 or directly from job.
   - `PUT /api/v1/applications/{id}/status`: Update lifecycle status (`draft`, `applied`, `interviewing`, `offer`, `rejected`, `archived`).
   - `POST /api/v1/applications/{id}/notes`: Add chronological application notes.
3. Dedicated `/applications` frontend page:
   - Clean Kanban / list view tracking opportunity status pipeline.
   - Quick link to view submitted tailored resume version and download exact submitted PDF.
   - Stage 5 "Log Application" CTA button.

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
