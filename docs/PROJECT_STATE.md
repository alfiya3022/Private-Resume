# PrivateResume - Current Project State

## Project phase
Epic 0 - Project Foundation Complete. Ready for Epic 1 - Authentication & User Isolation.

## Current status
- Git repository initialized.
- Full documentation suite (23 `.md` files) and QA workbooks (`PrivateResume_Manual_Test_Cases.xlsx`, `PrivateResume_Automation_Test_Cases.xlsx`) integrated under `docs/`.
- FastAPI modular backend scaffolded with Pydantic Settings, SQLAlchemy database engine, Alembic configuration, and `/api/v1/health` subsystem health monitor.
- Backend smoke tests passing (`pytest` verified: root endpoint and health check passing).
- React + Vite + Tailwind CSS frontend configured with locked visual language (warm cream base `#FAF8F5`, charcoal typography, coral primary actions, subtle borders, four locked top-level areas).
- Frontend production build passing (`vite build` compiled cleanly with 0 errors).
- Docker Compose configured for PostgreSQL (with persistent volume `postgres_data`), FastAPI (with LaTeX runtime), and React.
- Host runtimes verified: Ollama v0.40.4 and MiKTeX pdfTeX available.

## Current next step
Epic 1 - Authentication & User Isolation.
Tasks: User model, password hashing (bcrypt), JWT token/session management, `/api/v1/auth` endpoints (register, login, me), auth dependency, and user isolation tests.

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
None. Epic 0 foundation verified.
