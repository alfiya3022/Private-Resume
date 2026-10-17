# PrivateResume - Technology Stack

## Locked V1 stack

| Area | Technology | Reason |
|---|---|---|
| Frontend | React | Component-based UI appropriate for the product's interactive workspace |
| Build tool | Vite | Fast, straightforward React development setup |
| Language | JavaScript | Matches the frozen project stack and keeps V1 focused |
| Styling | Tailwind CSS | Consistent implementation of the locked design system with low CSS overhead |
| Backend | Python + FastAPI | Strong fit for API development and Python-based AI/document workflows |
| Validation | Pydantic | Explicit request/response validation and typed data contracts |
| ORM | SQLAlchemy | Relational data access with separation between DB models and API schemas |
| Migrations | Alembic | Controlled database schema evolution |
| Database | PostgreSQL | Relational core with strong constraints, relationships, and transactions |
| AI runtime | Ollama | Local-first inference and privacy-oriented architecture |
| PDF parsing | PyMuPDF | Direct PDF text extraction for the V1 source resume flow |
| Resume generation | LaTeX | Deterministic, controlled formatting using the candidate's template |
| Backend tests | Pytest | Unit/integration coverage for Python APIs |
| E2E | Playwright | Browser-level verification of critical user journeys |
| API exploration | Postman | Manual endpoint exploration and debugging before/alongside automation |
| VCS | Git + GitHub | Version history, feature branches, PR workflow, portfolio visibility |
| Containers | Docker + Docker Compose | Reproducible FastAPI/PostgreSQL development environment |
| CI | GitHub Actions | Automated checks on push/PR |
| File storage | Local filesystem | Simple V1 implementation consistent with local-first product goals |

## Application-level Docker strategy
```text
React       -> Docker
FastAPI     -> Docker
PostgreSQL  -> Docker + persistent volume
LaTeX       -> included in the backend Docker image
Ollama      -> local/native
```

### Why
PrivateResume is intended to be reproducible on another compatible machine. Docker therefore packages the application runtime for React and FastAPI, the PostgreSQL service, and the LaTeX compiler used by resume generation. Ollama remains native because local model execution can depend on host GPU/driver support and model storage.

During development, running React locally with Vite is allowed when it improves iteration speed; the Docker Compose setup remains the reproducible application environment.

## Testing tools
- Pytest: unit and backend/database integration tests.
- Postman: manual API exploration, contract checks, negative scenarios, and repeatable collections.
- Playwright: critical browser end-to-end and browser regression coverage.
- GitHub Actions: automated checks on pushes and pull requests.

HTTPX is not a required project test tool at this stage.

## Deliberately excluded unless later justified
Redis, Celery, Kafka, Kubernetes, Terraform, MongoDB, GraphQL, Elasticsearch, vector databases, LangChain, LangGraph, and microservices.

### Why
No current V1 requirement demonstrates enough value to justify the operational and conceptual complexity these technologies introduce.

## TBD decisions
- Exact Ollama model: benchmark and select later.
- Authentication implementation details: likely JWT, but not locked yet.
- Deployment target: intentionally TBD because the V1 product is local-first.

## Dependency policy
Add dependencies only when they provide meaningful value that would otherwise require substantial in-house maintenance. Verify compatibility, then freeze the working dependency set.
