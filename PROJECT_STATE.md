# PrivateResume - Current Project State

## Project phase
Epic 5 - Resume-to-Job Matching Complete. Ready for Epic 6 - Tailored Resume + Human Editing.

## Current status
- Git repository and foundation verified (Epic 0).
- User authentication, JWT tokens, and user isolation verified (Epic 1).
- Candidate master profile & PyMuPDF resume ingestion verified (Epic 2).
- Job management & Workspace Stage 1 intake engine verified (Epic 3).
- Local-first JD Analysis & requirements extraction engine verified (Epic 4).
- Resume-to-Job Matching & Evidence alignment engine verified (Epic 5):
  - Deterministic matching engine (`MatchingService`) implementing transparent, explainable 4-category classification:
    - Matched Skills (backed by candidate profile and verified projects/experience)
    - Weakly Represented Skills (present in profile but lacking dedicated project evidence)
    - Missing Skills (explicitly flagged with non-fabrication notice)
    - Unsupported Claims (candidate claims lacking verifiable project backing)
  - Estimated Job Match metric calculated with 70% required / 30% preferred skill weights (strictly not labeled an ATS score).
  - Evidence citations mapping matched requirements directly to project and employment records.
  - SQLAlchemy relational model `MatchAnalysis` storing match scores, classification sets, and evidence maps.
  - REST endpoints operational under `/api/v1/jobs`:
    - `POST /jobs/{job_id}/match` (200 OK returning `MatchAnalysisResponse`)
    - `GET /jobs/{job_id}/match` (200 OK; 404 for missing or unauthorized access)
  - Alembic migration `005_create_match_tables.py` created.
  - 33 total automated Pytest tests passing (100% pass rate across unit, API contracts, negative validation, and security isolation tests).
  - React Workspace Stage 3 integrated: displays Estimated Job Match card, 4-category skill alignment cards, interactive evidence citations, non-fabrication warning banner, and transition to Stage 4.
  - Both QA test workbooks updated with actual execution records:
    - `docs/PrivateResume_Automation_Test_Cases.xlsx` (`Auth`, `Master_Resume`, `Profile_Personal`, `Workspace_Job_Input`, `JD_Analysis`, `Match_Analysis`, `Evidence`: 33 automated tests logged)
    - `docs/PrivateResume_Manual_Test_Cases.xlsx` (`Auth`, `Master_Resume`, `Workspace_Job_Input`, `JD_Analysis`, `Match_Analysis`, `Evidence`: 12 manual tests logged)

## Current next step
Epic 6 - Tailored Resume + Human Editing.
Tasks:
1. Tailored resume entity (`TailoredResume`) and version history (Draft v1, v2, Final style).
2. Section-level content model (Summary, Skills, Experience, Projects, Education, Certifications).
3. "Ask AI" section editing flow with structured diffs (accept, reject, edit manually).
4. Resume tailoring service (`app/services/tailoring_service.py`).
5. Endpoints:
   - `POST /api/v1/jobs/{job_id}/tailor`
   - `GET /api/v1/tailored-resumes/{id}`
   - `POST /api/v1/tailored-resumes/{id}/edit`
   - `PUT /api/v1/tailored-resumes/{id}`
6. Frontend Stage 4 Tailored Resume interactive editor with Ask AI drawer and version dropdown.

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
