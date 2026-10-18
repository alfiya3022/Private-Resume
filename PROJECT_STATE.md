# PrivateResume - Current Project State

## Project phase
Epic 7 - LaTeX + PDF Generation Complete. Ready for Epic 8 - Resume Validation Engine.

## Current status
- Git repository and foundation verified (Epic 0).
- User authentication, JWT tokens, and user isolation verified (Epic 1).
- Candidate master profile & PyMuPDF resume ingestion verified (Epic 2).
- Job management & Workspace Stage 1 intake engine verified (Epic 3).
- Local-first JD Analysis & requirements extraction engine verified (Epic 4).
- Resume-to-Job Matching & Evidence alignment engine verified (Epic 5).
- Tailored Resume Generation, Versioning & Human Editing verified (Epic 6).
- LaTeX + PDF Generation & Document Streaming verified (Epic 7):
  - Controlled LaTeX injection engine (`LatexService`) with rigorous character escaping (`&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, `\`) preventing macro injection or compiler breakage.
  - Native ATS-compliant LaTeX template structure using core typography primitives, compiling in milliseconds without external network/package dependencies.
  - Isolated subprocess compiler invoking `pdflatex -interaction=nonstopmode -no-shell-escape` within temporary workspaces.
  - Relational `ResumeArtifact` model storing compiled PDF and TeX source files in isolated user storage (`storage/artifacts/{user_id}/`).
  - REST endpoints operational under `/api/v1/tailored-resumes`:
    - `POST /{resume_id}/generate-pdf`: Compiles PDF, returns artifact metadata.
    - `GET /{resume_id}/artifacts`: Lists generated documents and file sizes.
    - `GET /{resume_id}/pdf`: Streams binary `application/pdf` for inline preview or download.
    - `GET /{resume_id}/tex`: Streams LaTeX source file for inspection.
  - Alembic migration `007_create_artifact_tables.py` created and applied.
  - 40 total automated Pytest tests passing (100% pass rate).
  - Workspace Stage 5 UI integrated:
    - Real-time inline PDF preview (`<iframe>`).
    - Direct "Download PDF" and "LaTeX Source" actions.
    - Fullscreen document viewer trigger and compilation refresh.
  - UI content decluttered: streamlined banners and cards across Stages 3, 4, and 5 for a clean, professional aesthetic.
  - Both QA test workbooks updated with actual execution records:
    - `docs/PrivateResume_Automation_Test_Cases.xlsx` (43 automated tests logged across all modules)
    - `docs/PrivateResume_Manual_Test_Cases.xlsx` (19 manual tests logged across all modules)

## Current next step
Epic 8 - Resume Validation Engine.
Tasks:
1. Validation service (`app/services/validation_service.py`):
   - Text extractability check (ensures PDF contains selectable, parsable text).
   - Standard section heading presence (Summary, Experience, Education, Skills).
   - Contact details detection (email, phone, name).
   - Placeholder & template artifact check (detecting unresolved `TODO`, `[Company]`, `Lorem ipsum`).
   - Content integrity check ensuring zero unsupported claims.
2. Endpoints:
   - `POST /api/v1/tailored-resumes/{id}/validate`
   - `GET /api/v1/tailored-resumes/{id}/validation`
3. Frontend Stage 5 Validation checklist panel with pass/warn/fail status cards.

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
