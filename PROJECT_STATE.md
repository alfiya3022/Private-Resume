# PrivateResume - Current Project State

## Project phase
Epic 11 - Final Polish, Documentation & Docker Packaging Complete. All Project Epics (0 through 11) 100% Complete & Verified.

## Current status
- **Epic 0 — Foundation**: Git repo, React Vite Tailwind frontend, FastAPI modular monolith, PostgreSQL, Docker Compose, root documentation.
- **Epic 1 — Auth & User Isolation**: Bcrypt passwords, JWT bearer tokens, user registration/login, user isolation middleware.
- **Epic 2 — Master Profile & PDF Ingestion**: PyMuPDF extraction, candidate profile CRUD (personal, skills, experience, projects, education, certifications), file upload storage.
- **Epic 3 — Job Intake Engine**: Job entity, status lifecycle, Workspace Stage 1 intake selector and saved job manager.
- **Epic 4 — Structured JD Analysis**: Local Ollama extraction with deterministic fallback, categorized requirements.
- **Epic 5 — Resume-to-Job Matching**: Deterministic 4-category classification, Estimated Job Match (0-100%), evidence citations, anti-fabrication rules.
- **Epic 6 — Tailoring & Human Editing**: `TailoredResume` model with version immutability (`v1` $\to$ `v2` $\to$ `v3`), Ask AI section refinement under anti-fabrication constraints, Workspace Stage 4 editor.
- **Epic 7 — LaTeX + PDF Generation**: Controlled LaTeX escaping engine, clean ATS LaTeX template, isolated subprocess compilation, `ResumeArtifact` persistence, inline document streaming.
- **Epic 8 — Resume Validation Engine**: ATS pre-flight engine (`ValidationService`) evaluating 6 objective checks (PDF health, text extractability, contact info, headings, placeholders, evidence grounding), interactive Stage 5 Quality Gate panel.
- **Epic 9 — Application Tracking Engine & Dashboard**: `Application` relational model, Alembic migration 009, dedicated `/applications` pipeline dashboard with status filtering and interview notes, 1-click Workspace Stage 5 logging.
- **Epic 10 — Testing, CI Pipeline & Security Hardening**: GitHub Actions CI workflow (`.github/workflows/ci.yml`), `SecurityHeadersMiddleware` (X-Content-Type-Options, X-Frame-Options: SAMEORIGIN), Playwright E2E browser test suite.
- **Epic 11 — Final Polish, Documentation & Packaging**: Production multi-container Docker Compose configuration, idempotent database seed utility (`backend/seed.py`), sleek clutter-free neo-brutalist UI polish, and comprehensive production README documentation.
- **Epic 12 — User Experience Polish & Stage 4/5 Refinements**:
  - Full inline Edit & Save CRUD for Projects and Experience in Profile tab.
  - Native `<input type="date">` calendar selectors for all historical dates.
  - LaTeX Template Package Manager accepting `.zip` packages only, with compiler line removed.
  - INR currency auto-formatting (`₹ 12,00,000`) for Opportunity compensation.
  - Anti-hallucination JD experience extraction defaulting strictly to "Not specified" if unspecified.
  - Stage 4 Progressive Tailoring Studio with full CRUD & inline Save buttons for every line (Resume Heading, Summary, Skills categories/items, Experience roles/bullets, Projects/bullets, Education & Certifications).
  - Stage 5 clean "5. PDF" generation tab with audit health panel removed, MiKTeX compiler banner removed, terminal/black window removed, re-compile option removed, and reliable authenticated PDF download with automatic logging into the Applications tracker.
- **Epic 13 — Template Engine Personalization, Multi-Cycle Isolation & Clean Flow**:
  - Candidate-provided LaTeX template engine: Automatically renders resumes using candidate's uploaded `.tex` or `.zip` template; cleanly falls back to system base template when removed.
  - Education & Certification inline CRUD: Added full inline Edit and Save functionality to Education and Certification cards in Candidate Profile.
  - Seamless Stage 4 to Stage 5 transition: Eliminated direct download/audit modal popups upon clicking "Proceed to Stage 5: PDF", rendering the PDF preview directly in the viewer.
  - Clean workspace multi-cycle isolation: Downloading a PDF auto-logs the opportunity to the Applications pipeline and fully wipes active workspace draft state so prior content never spills over into subsequent applications.
- **Epic 14 — Compilation Hardening, Comprehensive JD Extraction & UI Streamlining**:
  - LaTeX Compilation Resilience: Resolved pdflatex process hangs by adding `-halt-on-error` and `-disable-installer` flags, and injecting self-contained shims for `hyperref` and `parskip` packages to eliminate network CTAN calls and interactive prompts.
  - Custom Template Compatibility: Added native regex support for `\begin{rSection}` environments (FAANGpath and modern CV templates) in `_inject_into_custom_template` so custom uploaded templates receive tailored content seamlessly.
  - UI Simplification: Completely removed the "Categorized Technical Stack" section from Stage 2 (Job Requirements Analysis) per user request.
  - Precision JD Scraping: Vastly expanded tech taxonomy for database roles, administration, protocols, data querying, and scripting; added intelligent sentence-level required vs. preferred classification and accurate experience-year parsing.

## Completion standard
- Backend & frontend servers actively running and healthy (FastAPI on 8005, Vite on 5173).
- Frontend production bundle cleanly built with Vite (`npm run build`).
- PDF compilation verified working in under 1 second without timing out.
- JD extraction verified extracting comprehensive skillsets and accurate years.
- All constitutional rules and architecture constraints respected (local-first, zero telemetry, non-fabrication, version immutability, modular monolith).

## Current next step
Ready for end-user testing and production usage at `http://localhost:5173`.

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
