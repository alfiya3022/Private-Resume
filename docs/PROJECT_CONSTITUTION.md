# PrivateResume - Project Constitution

## Purpose
This document is the compact baseline for the project's approved product and engineering rules. Detailed documentation lives under `docs/`.

## Product
PrivateResume is a privacy-first, local-first AI-powered resume tailoring and job application management platform for job seekers.

## Core principle
AI recommends -> Candidate reviews -> Candidate edits/approves -> System generates.

The system may optimize representation of genuine qualifications but must not fabricate skills, experience, projects, certifications, achievements, qualifications, or metrics.

## Top-level product areas
1. Auth
2. Profile
3. Workspace
4. Applications

Workspace is a progressive workflow, not a single giant scrolling page.

## Architecture
Modular monolith. React frontend communicates with FastAPI; backend communicates with PostgreSQL, local Ollama, local storage, and LaTeX.

## Locked V1 stack
React, Vite, JavaScript, Tailwind CSS, Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Alembic, Ollama, PyMuPDF, LaTeX, Pytest, HTTPX, Playwright, Postman, Git/GitHub, Docker/Docker Compose, GitHub Actions.

## Runtime placement
- React -> Docker application environment; local Vite development allowed for fast iteration
- FastAPI -> Docker
- PostgreSQL -> Docker + persistent volume
- Ollama -> local/native
- LaTeX -> included in backend Docker image

## UI direction
Warm cream/off-white, charcoal typography, thin dark borders, coral primary actions, pastel statuses, generous whitespace, editorial/modern neo-brutalist SaaS influence, polished and professional.

## Important invariants
- Frontend never directly accesses PostgreSQL or Ollama.
- Historical tailored resume versions are immutable.
- Applications reference the exact resume version submitted.
- Matching is primarily deterministic after structured extraction.
- Estimated Job Match is not an employer ATS score.
- ATS Compatibility is presented as concrete checks.

## Deliberately excluded unless approved
Redis, Celery, Kafka, Kubernetes, Terraform, MongoDB, GraphQL, Elasticsearch, vector databases, LangChain, LangGraph, microservices, and autonomous job applications.

## Change control
Do not change a locked decision casually. Reopen a decision only when a real requirement, constraint, or verified implementation issue justifies reconsideration. Record the context, alternatives, trade-off, and new decision.
