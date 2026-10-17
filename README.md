# PrivateResume

PrivateResume is a privacy-first, local-first AI-powered resume tailoring and job application management platform. It helps candidates analyze job descriptions, compare requirements with genuine candidate evidence, generate evidence-based tailored resumes, produce a controlled PDF through a LaTeX template, validate the result, and track applications.

## Core Principle
AI recommends -> Candidate reviews -> Candidate approves -> System generates.
*Never fabricate qualifications or experience.*

## Main Architecture
```text
React -> FastAPI -> PostgreSQL
             |
             +-> Ollama (local)
             +-> local files
             +-> LaTeX
```

## Tech Stack
React, Vite, JavaScript, Tailwind CSS, Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Alembic, Ollama, PyMuPDF, LaTeX, Pytest, Playwright, Postman, Git/GitHub, Docker, Docker Compose, GitHub Actions.

## Product Areas
1. **Auth**: User registration, login, JWT token authentication, and data isolation.
2. **Profile**: Structured candidate profile (Education, Experience, Projects, Skills, Template) and master resume parsing.
3. **Workspace**: Progressive step-by-step workflow (Add Inputs -> Analyze JD -> Match Evidence -> Tailor & Edit -> Generate & Validate).
4. **Applications**: Application tracking with direct linkage to the exact immutable tailored resume version.

## Quick Start (Docker)
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Start the services with Docker Compose:
   ```bash
   docker compose up --build
   ```
3. Open the frontend at `http://localhost:5173` and backend API documentation at `http://localhost:8000/docs`.

## Quick Start (Local Development)
- **Backend**:
  ```bash
  cd backend
  python -m venv venv
  venv\Scripts\activate  # Windows (or source venv/bin/activate on Unix)
  pip install -r requirements.txt
  uvicorn app.main:app --reload
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## Documentation
Comprehensive project specifications, architecture records, test plans, and test case workbooks are located in `docs/`:
- `docs/PROJECT_STATE.md`: Current verified implementation state
- `docs/AGENTS.md`: AI coding rules and constraints
- `docs/DEVELOPMENT_PLAN.md`: Phased epic-by-epic implementation roadmap
- `docs/API_SPEC.md`: REST API endpoint specification
- `docs/DATABASE_DESIGN.md`: Entity relationships and schemas
- `docs/DESIGN_SPEC.md`: Visual and interaction specifications
- `docs/PrivateResume_Manual_Test_Cases.xlsx`: Manual test cases workbook
- `docs/PrivateResume_Automation_Test_Cases.xlsx`: Automated test cases workbook
