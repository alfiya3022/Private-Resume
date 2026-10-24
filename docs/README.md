# PrivateResume - Documentation Overview

PrivateResume is a privacy-first, local-first AI-powered resume tailoring and job application management platform. It enables candidates to ingest master resumes, analyze job descriptions, evaluate evidence-grounded matches, tailor resumes progressively, compile ATS-compliant PDFs via local LaTeX, and manage their job application pipeline.

---

## Core Principle
**AI Recommends ──► Candidate Reviews ──► Candidate Approves ──► System Generates**

- Strictly zero fabrication: candidate profile facts are the sovereign ground of truth.
- Local-first architecture: PostgreSQL, Ollama AI, and LaTeX execute locally on the host machine.
- Zero telemetry: no PII or resume bullets ever touch external third-party cloud APIs.

---

## High-Level Architecture
```text
React 18 Frontend (Vite + Tailwind CSS)
       │ HTTP / REST (JWT Bearer)
       ▼
FastAPI Modular Monolith Backend
       ├── PostgreSQL 15 (Docker Container: private-resume-db on Port 5433)
       ├── Ollama Local AI (qwen3:4b-instruct on Port 11434)
       ├── Consolidated Local Storage (backend/storage: Resumes, Artifacts, Templates)
       └── Subprocess pdflatex (-halt-on-error -disable-installer -no-shell-escape)
```

---

## Four Top-Level Product Areas
1. **Auth (`/auth`)**: JWT bearer tokens, Bcrypt password hashing, row-level multi-tenant data isolation.
2. **Profile (`/profile`)**: Candidate Master Profile (Experience, Projects, Skills, Education, Certifications) with inline CRUD + Personal LaTeX Template Package Manager (`.tex` / `.zip`).
3. **Workspace (`/`)**: 5-Stage Progressive Tailoring Engine (Job Intake, Requirements Analysis, Match Evidence, Tailoring Studio, and Instant PDF Preview & Download).
4. **Applications (`/applications`)**: Multi-status Kanban application tracker (`saved`, `applied`, `assessment`, `interview`, `rejected`, `offer`, `withdrawn`) with linked immutable resume snapshots.

---

## Documentation Navigation
- [`DOCUMENTATION_INDEX.md`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/DOCUMENTATION_INDEX.md) — Directory index of all engineering and product specifications.
- [`ARCHITECTURE.md`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/ARCHITECTURE.md) — System boundaries, data flow pipelines, and LaTeX compiler security.
- [`API_SPEC.md`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/API_SPEC.md) — Complete REST API contract and endpoint schema documentation.
- [`DATABASE_DESIGN.md`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/DATABASE_DESIGN.md) — PostgreSQL relational schema, constraints, and entity relationships.
- [`DEVELOPMENT_PLAN.md`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/DEVELOPMENT_PLAN.md) — Completed milestones (Epics 0 through 14) and Definition of Done.
- [`PROJECT_STATE.md`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/PROJECT_STATE.md) — Current verified implementation status and test metrics.
- [`CHANGELOG.md`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/CHANGELOG.md) — Release notes and version history.
- [`SECURITY.md`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/SECURITY.md) — Threat models, security headers, and data isolation controls.
