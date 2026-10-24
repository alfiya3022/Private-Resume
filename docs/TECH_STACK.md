# PrivateResume - Technology Stack Specification

**Locked V1 Baseline**  
Every technology in this stack has been validated, integrated, and verified against functional requirements and automated testing suites.

---

## 1. Locked Technology Choices & Rationale

| Layer | Technology | Version | Architectural Rationale |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | React | 18.3+ | Component-driven UI architecture suited for interactive multi-stage progressive tailoring. |
| **Bundler & Tooling** | Vite | 5.4+ | Lightning-fast Hot Module Replacement (HMR) and optimized production bundle compilation. |
| **Styling Engine** | Tailwind CSS | 3.4+ | Utility-first CSS implementing the locked neo-brutalist editorial design system with zero runtime overhead. |
| **Icons** | Lucide React | 0.344+ | Clean, accessible vector icons matching editorial typography. |
| **Backend Framework** | FastAPI | 0.110+ | High-performance asynchronous Python framework with native OpenAPI schema generation. |
| **Data Validation** | Pydantic | V2 | Strict type enforcement, payload serialization, and declarative data contracts. |
| **ORM / Database Layer**| SQLAlchemy | 2.0+ | Enterprise-grade Object-Relational Mapping with connection pooling and typed queries. |
| **Schema Migrations** | Alembic | 1.13+ | Version-controlled, deterministic database schema evolution. |
| **Primary Database** | PostgreSQL | 15 (Alpine) | ACID-compliant relational core with JSONB support, constraints, and foreign key cascades. |
| **Local AI Inference** | Ollama | Latest (`qwen3:4b-instruct`) | Local-first Large Language Model inference guaranteeing 100% privacy and zero telemetry. |
| **PDF Extraction** | PyMuPDF + PyMuPDF4LLM | 1.28+ (1.24+ req) | Ultra-fast local C-level PDF parsing and layout-aware Markdown extraction with clean normalization. |
| **Document Typesetting**| LaTeX (pdflatex) | MiKTeX / pdfTeX | Industry-standard deterministic typesetting guaranteeing ATS-parsable, selectable vector text. |
| **Unit & Integration** | Pytest | 8.0+ | Layered testing framework verifying API contracts, auth isolation, and parsing logic. |
| **E2E Browser Testing** | Playwright | 1.42+ | Cross-browser automated verification for critical candidate workflows. |
| **Containerization** | Docker + Compose | 3.8 Spec | Portable, reproducible multi-container deployment for PostgreSQL, backend, and frontend. |
| **CI / CD Pipeline** | GitHub Actions | Workflows v4 | Automated linting, build verification, and test execution on push and pull request. |
| **Local Storage** | Host Filesystem | `backend/storage` | Zero-cloud-dependency file persistence for source resumes, templates, and generated artifacts. |

---

## 2. Docker & Container Deployment Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                      Docker Compose                         │
├─────────────────┬────────────────────┬──────────────────────┤
│    Frontend     │      Backend       │       Database       │
│  React 18 / Nginx│  FastAPI (Python)  │  PostgreSQL 15       │
│  (Port 5173)    │  (Port 8000/8005)  │  (Port 5433:5432)    │
└─────────────────┴─────────┬──────────┴──────────┬───────────┘
                            │                     │
                            ▼                     ▼
                     ┌──────────────┐     ┌───────────────┐
                     │ Native Host  │     │ Persistent    │
                     │    Ollama    │     │ Docker Volume │
                     │ (Port 11434) │     │(postgres_data)│
                     └──────────────┘     └───────────────┘
```

- **Frontend & Backend**: Containerized for production deployment; local Vite and Uvicorn development are supported for rapid feedback loops.
- **PostgreSQL**: Runs inside a dedicated container with a named persistent volume (`postgres_data`) ensuring data survives restarts.
- **Ollama**: Runs natively on the host machine to leverage hardware acceleration (GPU/Metal/CUDA) and existing model weights without container overhead.

---

## 3. Deliberately Excluded Technologies (Constitutional Non-Goals)

To preserve architectural simplicity, reduce operational friction, and avoid unnecessary abstractions, the following technologies are **deliberately excluded**:
- **Redis / Celery / Kafka**: Background processing is handled natively via FastAPI background tasks and local subprocesses. No message broker is required for a single-user or small-team local workflow.
- **Kubernetes / Terraform / Helm**: Over-engineering for a local-first application. Docker Compose provides all required orchestration.
- **MongoDB / DynamoDB**: The core domain is inherently relational (User $\to$ Profile $\to$ Job $\to$ Tailored Resume $\to$ Application). Relational constraints prevent data corruption.
- **GraphQL**: REST under `/api/v1` provides simple, predictable contracts with OpenAPI documentation.
- **Vector Databases / LangChain / LangGraph**: Heavy frameworks introduce instability, high token costs, and prompt bloat. PrivateResume uses lightweight, direct Ollama HTTP client interactions with deterministic fallback engines.
