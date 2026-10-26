# Verity - AI Coding Agent Instructions

## Authority

Read `PROJECT_STATE.md` first. Read the relevant documentation before changing architecture, API contracts, database design, or UI structure.

## Core rule

Do not casually change a locked decision. If a change would affect an accepted architectural, product, design, or technology decision, stop and explicitly propose reopening it.

## Product principles

- Local-first and privacy-first by default.
- AI recommends; candidate reviews; candidate approves.
- Never fabricate qualifications or experience.
- Missing skills are not instructions to invent skills.
- Historical resume versions are immutable.

## Architecture constraints

- Modular monolith.
- React frontend never talks directly to PostgreSQL or Ollama.
- Business logic belongs in backend services, not route handlers.
- Matching remains primarily deterministic after structured extraction.

## Frozen V1 stack

React, Vite, JavaScript, Tailwind CSS, Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Alembic, Ollama, PyMuPDF, LaTeX, Pytest, Playwright, Postman, Git/GitHub, Docker/Docker Compose, GitHub Actions.

## Avoid unless explicitly approved

Redis, Celery, Kafka, Kubernetes, Terraform, MongoDB, GraphQL, Elasticsearch, vector databases, LangChain, LangGraph, microservices.

## Development behavior

- Keep changes focused on the current task.
- Do not rewrite unrelated code.
- Prefer simple solutions over unnecessary abstractions.
- Add tests for behavior changes.
- Preserve API contracts.
- Explain why a new dependency or pattern is necessary before adding it.
- Do not place secrets or sensitive resume content in logs.

## Documentation behavior

After a meaningful milestone, update `PROJECT_STATE.md` with verified work only. Update decision documents only when a decision is intentionally changed. Do not invent project history.

## Continuous Documentation Subagent

The `docs-updater` subagent is strictly prompt-driven: it is automatically invoked after every user prompt, code change, and verified result to inspect changes and ensure `docs/`, `PROJECT_STATE.md`, `CHANGELOG.md`, `README.md`, and test-case workbooks remain continuously synchronized with verified work. It operates under a strict documentation-only scope and does not modify application source code.

## Continuous Ponytail Subagent

The `ponytail-reviewer` subagent is automatically invoked in the background whenever code changes are made. It audits code against Ponytail principles: enforcing the smallest complete change, YAGNI, standard library / native patterns first, zero bloat, and flagging edge-case risks.

## Completion standard

A task is not complete when code merely exists. It is complete when the requirement is satisfied, relevant tests pass, edge/error handling is addressed, and the implementation is consistent with the project documents.

## Testing governance

Use industry-style layered testing throughout development. Do not postpone all testing to the end.

For a meaningful feature, determine the appropriate combination of:

- unit testing
- integration testing
- API/manual testing
- UI/E2E testing
- negative/edge testing
- security testing
- regression testing
- smoke testing when warranted

Do not run verification commands merely for reassurance. Run focused commands when the setup/acceptance criteria require them or when diagnosing a real issue.

When repository/code content is needed and it is not already available in context, request the specific file or relevant section instead of repeatedly retrieving large files.

## Test case logging

After completing a feature's required testing and before the feature is merged, update the appropriate manual and/or automation test-case workbook tabs with the actual results.

Do not claim tests were executed unless they were actually executed.
