# PrivateResume

PrivateResume is a privacy-first, local-first AI-powered resume tailoring and job application management platform. It helps candidates analyze job descriptions, compare requirements with genuine candidate evidence, generate evidence-based tailored resumes, produce a controlled PDF through a LaTeX template, validate the result, and track applications.

## Core principle
AI recommends -> Candidate reviews -> Candidate approves -> System generates.

## Main architecture
```text
React -> FastAPI -> PostgreSQL
             |
             +-> Ollama (local)
             +-> local files
             +-> LaTeX
```

## Tech stack
React, Vite, JavaScript, Tailwind CSS, Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Alembic, Ollama, PyMuPDF, LaTeX, Pytest, Playwright, Postman, GitHub, Docker, Docker Compose, GitHub Actions.

## Product areas
- Auth
- Profile
- Workspace
- Applications

## Development status
The planning and design baseline is locked. Epic 0 - Project Foundation is the next implementation phase.

## Documentation
See `docs/` for product, design, architecture, API, database, engineering, security, and decision documents.

See `AGENTS.md` for AI coding-agent rules and `PROJECT_STATE.md` for the current verified implementation state.

## Local-first note
The product is designed to keep AI processing local by default through Ollama. Local-first is a product posture, not a guarantee against every form of local-device risk.
