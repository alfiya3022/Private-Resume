# PrivateResume - Current Project State

## Project phase
Epic 1 - Authentication & User Isolation Complete. Ready for Epic 2 - Profile + Master Resume.

## Current status
- Git repository and foundation verified (Epic 0).
- User authentication and authorization engine implemented and verified (Epic 1):
  - SQLAlchemy `User` entity with email uniqueness, bcrypt password hashing (12 rounds), active status, and timestamps.
  - JWT token generation, expiration, and payload decoding via `python-jose`.
  - Pydantic models for registration, login, token output, and user profile response.
  - Service layer `AuthService` handling registration, lookup, and password authentication.
  - FastAPI dependency `get_current_user` enforcing bearer token validation and user identity.
  - Endpoints operational under `/api/v1/auth`:
    - `POST /register` (201 Created, duplicate email rejection with 409 Conflict)
    - `POST /login` (200 OK with bearer access token, 401 on bad credentials)
    - `GET /me` (200 OK with authenticated user profile, 401 on missing/invalid token)
  - Alembic migration `001_create_users_table.py` created.
  - Full automated Pytest suite passing (14 tests passed, including unit, API, negative, and user isolation tests).
  - Frontend authentication flow connected: registration, login, token persistence in localStorage, active user banner, and logout.
  - Both QA test workbooks updated with actual execution records:
    - `docs/PrivateResume_Automation_Test_Cases.xlsx` (`Auth` sheet: 12 tests passed)
    - `docs/PrivateResume_Manual_Test_Cases.xlsx` (`Auth` sheet: 3 tests passed)

## Current next step
Epic 2 - Profile + Master Resume.
Tasks:
1. Candidate profile entity & relational models (Personal info, Education, Experience, Projects, Skills, Certifications, Template).
2. Master resume upload (multipart PDF upload with PyMuPDF text extraction).
3. Section detection and candidate data structuring.
4. Profile CRUD API endpoints (`/api/v1/profile`, `/api/v1/resumes`).
5. Frontend Profile Workspace integration with section-by-section review and editing.

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
None. Epics 0 and 1 verified and passing.
