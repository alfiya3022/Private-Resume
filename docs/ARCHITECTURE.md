# PrivateResume - Architecture Specification

**Style**: Modular Monolith  
**Posture**: Local-First, Privacy-First, Zero External Telemetry  
**Stack**: React 18 (Vite) + FastAPI (Python 3.10+) + PostgreSQL 15 + Ollama (`qwen3:4b-instruct`) + LaTeX (MiKTeX/pdfTeX)

---

## 1. Architectural Style & Rationale

PrivateResume is structured as a **Modular Monolith**. The application operates as a single deployable backend service organized into strictly separated internal domain modules.

### Why a Modular Monolith?
- **Domain Cohesion**: The platform manages tightly interrelated entities (Candidate Profile, Master Resumes, Job Opportunities, Tailored Versions, Artifacts, and Applications) that benefit from ACID database transactions and shared relational schemas.
- **Local-First Simplicity**: Minimizes operational friction. A candidate can run the entire system on a personal machine without managing service discovery, distributed tracing, network latency, or message brokers.
- **Zero Telemetry**: Sensitive resume data, contact info, and employer histories remain strictly on the user's host machine.

### Explicit Non-Goals
No distributed microservices, no Kafka/RabbitMQ message brokers, no Redis caching, and no external AI API wrappers (OpenAI, Anthropic).

---

## 2. High-Level System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                         │
│             React 18 + Vite + Tailwind CSS                  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / REST (JWT Bearer)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend Service                    │
│   (SecurityHeadersMiddleware, Auth Router, Module Routers)  │
├──────────────────────────────┬──────────────────────────────┤
│      Business Services       │       Engine Pipelines       │
│  - AnalysisService           │  - PyMuPDF Ingestion Engine  │
│  - MatchingService           │  - Deterministic JD Scraper  │
│  - TailoringService          │  - LaTeX AST Injector        │
│  - ApplicationService        │  - pdflatex Subprocess       │
└──────┬────────────────┬──────┴───────────────┬──────────────┘
       │                │                      │
       ▼                ▼                      ▼
┌──────────────┐ ┌──────────────┐ ┌───────────────────────────┐
│  PostgreSQL  │ │    Ollama    │ │     Local Filesystem      │
│  (Docker on  │ │ (Local Port  │ │  (backend/storage: PDFs,  │
│  Port 5433)  │ │    11434)    │ │   resumes, .tex templates)│
└──────────────┘ └──────────────┘ └───────────────────────────┘
```

**Key Boundary Rule**: The React frontend **never** connects directly to PostgreSQL or Ollama. All interactions flow through the FastAPI backend API contract under `/api/v1`.

---

## 3. End-to-End Processing Pipeline

The platform follows a unidirectional, multi-stage workflow:

```text
[Stage 1: Ingestion]
Master PDF ──► PyMuPDF + PyMuPDF4LLM ──► clean_resume_markdown ──► Section Detection ──► PostgreSQL Candidate Profile

[Stage 2: JD Analysis]
Raw JD Text ──► Ollama + Deterministic Taxonomy ──► Structured Requirements (Required, Preferred, Exp)

[Stage 3: Evidence Matching]
Profile Facts + Structured JD ──► Deterministic Classifier ──► 4-Category Evidence Matrix + Match %

[Stage 4: Progressive Tailoring]
Profile Truth + Evidence Matrix ──► Tailored Draft ──► Line-by-Line CRUD + AI Section Refine

[Stage 5: Compilation & Persistence]
Tailored Resume JSON ──► LaTeX AST Injection ──► pdflatex Sandbox ──► Output PDF & Tex Artifact

[Stage 6: Application Pipeline]
PDF Downloaded ──► Auto-log Application Tracker ──► Clean Workspace Isolation Reset
```

---

## 4. Module Responsibilities & Domain Boundaries

| Module | Core Responsibility | Persistence |
| :--- | :--- | :--- |
| **`auth`** | User registration, login, Bcrypt hashing, JWT issuance and token validation. | `users` table |
| **`profile`** | Structured source of truth for candidate data (experience, projects, skills, education). | `candidate_profiles`, `skills`, `experiences`, `projects`, `educations`, `certifications` |
| **`resumes`** | Ingestion, validation, and storage of source PDF resumes using PyMuPDF and PyMuPDF4LLM. | `master_resumes` table, `backend/storage/resumes` |
| **`jobs`** | Target opportunity intake, compensation tracking, and status lifecycle. | `jobs` table |
| **`analysis`** | Hybrid JD extraction: Ollama LLM structured prompt with deterministic fallback taxonomy. | `job_requirements` table |
| **`matching`** | Primarily deterministic evidence matching; calculates Estimated Job Match. | `match_analyses` table |
| **`tailoring`** | Orchestrates versioned drafts (`v1`, `v2`, `v3`) and line-level inline editing. | `tailored_resumes` table |
| **`latex`** | Custom template management, AST injection, subprocess compilation, and artifact generation. | `resume_artifacts` table, `backend/storage/artifacts` |
| **`applications`**| Pipeline tracking (Applied, Interview, Offer) linked to exact resume version. | `applications` table |

---

## 5. AI Service Boundary & Constitutional Anti-Fabrication

The AI subsystem operates within strict constitutional guardrails:
1. **Candidate Profile As Sovereign Truth**:
   The candidate's verified profile is the sole ground of truth. Missing skills identified during JD matching are treated as developmental gaps—**never** as instructions to fabricate experience.
2. **Deterministic Precedence**:
   Evaluation metrics (Match %, missing skills, qualification checks) are calculated deterministically. AI is restricted to language comprehension and phrasing enhancement.
3. **Structured Boundary Abstraction**:
   All AI communication passes through `OllamaProvider` using strict JSON schemas. If Ollama is unreachable or times out, the system seamlessly falls back to high-accuracy deterministic extraction.

---

## 6. Hardened LaTeX Compilation Engine

The compilation engine in [`latex_service.py`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/backend/app/services/latex_service.py) enforces security, offline resilience, and template compatibility:

### 6.1 Subprocess Security Flags
```python
cmd = [
    "pdflatex",
    "-interaction=nonstopmode",  # Never prompt interactively
    "-halt-on-error",            # Abort immediately on syntax error (zero hang)
    "-disable-installer",        # Prevent MiKTeX from hanging on CTAN network calls
    "-no-shell-escape",          # Strictly forbid execution of external shell binaries
    f"{output_base_name}.tex",
]
```

### 6.2 Self-Contained Shims & Resilience
- Custom templates referencing `\usepackage{hyperref}` or `\usepackage[parfill]{parskip}` automatically receive self-contained native TeX link macros (`\providecommand{\href}`) and spacing definitions. This ensures 100% offline compilation without missing package failures.

### 6.3 Universal Template AST Injection
- Supports both standard LaTeX document structures (`\section*{...}`) and custom class environments (e.g. `\begin{rSection}{...}` in FAANGpath and Trey Hunner templates).
- Automatically substitutes candidate metadata into `\name{...}`, `\author{...}`, and `\address{...}` headers.

---

## 7. Multi-Cycle Workspace Isolation & Candidate-Approved Tracking

To uphold candidate agency ("AI recommends; candidate reviews; candidate approves") and prevent application drafts from spilling over into new intake cycles:
1. **Decoupled PDF Download**: Downloading a compiled PDF strictly retrieves the PDF artifact for candidate inspection and submission. It does not automatically register applications or wipe the active workspace state.
2. **Explicit Candidate-Approved Tracking**: An explicit "Log to Tracker" button in Stage 5 empowers the candidate to deliberately log the opportunity and exact tailored resume version to the Applications pipeline when ready.
3. **Candidate-Initiated Intake Reset**: The workspace draft state is preserved during review and download. Resetting or transitioning to a new intake cycle is explicitly triggered by the candidate (via the header "New Job Intake" control or starting a new opportunity intake from Stage 1), preventing premature workspace wiping.
4. **Clean Intake Query**: `jobsApi.listJobs('active')` only loads unapplied jobs, ensuring every new intake cycle starts with a blank canvas and clean separation of concerns.
