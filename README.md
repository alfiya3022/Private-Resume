# PrivateResume

> **Privacy-First, Local-First AI-Powered Resume Tailoring & Application Platform**

PrivateResume empowers job seekers to analyze job descriptions, align real candidate evidence deterministically, progressively tailor high-density resumes, compile ATS-compliant PDFs via local LaTeX, and track the entire opportunity lifecycle — **with zero data leakage, zero hallucinations, and zero external telemetry**.

---

## 🏛️ Core Principles & Constitutional Rules

1. **AI Recommends · Candidate Approves · System Generates**: The candidate retains absolute veto and editorial control over every bullet, section, and claim.
2. **Strict Anti-Fabrication Guarantee**: Missing skills are honest gaps, never instructions to invent experience. Resume tailoring only highlights and re-orders verifiable candidate achievements.
3. **Version Immutability**: Historical resume versions (`v1`, `v2`, `v3`) are permanent, immutable snapshots. Modifying a finalized draft forks a new version to preserve submission history.
4. **Local-First & Private by Default**: Resume PDFs, PostgreSQL records, and local Ollama inference remain strictly on your machine. No third-party LLM APIs receive your sensitive career history.
5. **Deterministic ATS Compliance**: No fancy multi-column graphics or non-standard tables that confuse applicant tracking systems. Output is compiled through robust LaTeX typography primitives into selectable, machine-parsable PDF streams.

---

## 🛠️ Architecture & Tech Stack

```text
React 18 + Vite (Tailwind CSS Neo-Brutalist UI)
       │
       ▼ (REST API / Bearer JWT)
FastAPI Modular Monolith (Python 3.10+)
  ├── Core Security & Middleware (X-Frame-Options: SAMEORIGIN, CORS lockdown)
  ├── PyMuPDF & PyMuPDF4LLM Engine (Layout-aware text extraction & ATS audit)
  ├── Local Ollama Provider (Qwen / Local LLM with deterministic fallbacks)
  ├── Deterministic Match & Scoring Engine (0-100% Estimated Job Match)
  ├── Subprocess LaTeX Compiler (pdflatex -halt-on-error -disable-installer -no-shell-escape)
  └── PostgreSQL 15 (Docker on port 5433) & SQLAlchemy ORM (Alembic Migrations)
```

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React icons.
- **Backend**: FastAPI, Pydantic V2, SQLAlchemy 2, Alembic, PyMuPDF, PyMuPDF4LLM.
- **Database**: PostgreSQL 15 running in Docker (`private-resume-db` on port `5433`).
- **Local AI**: Ollama (`qwen3:4b-instruct` model on port `11434`).
- **Typesetting**: Native `pdflatex` (MiKTeX on Windows / TeX Live on Linux).
- **Testing**: Pytest (78 automated unit/integration tests), Playwright (E2E browser tests), GitHub Actions CI.

---

## 🚀 Quick Start

### 1. Start PostgreSQL (Docker)

```bash
docker compose up -d db
```

_(Runs PostgreSQL on port `5433` with persistent volume `postgres_data`)_.

### 2. Start Ollama (Local AI)

```bash
ollama serve
# Ensure qwen3:4b-instruct model is installed: ollama pull qwen3:4b-instruct
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows (or source venv/bin/activate on Unix)
pip install -r requirements.txt
alembic upgrade head             # Runs all migrations
python seed.py                   # Seeds demo account (demo@privateresume.local)
uvicorn app.main:app --host 127.0.0.1 --port 8005 --reload
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev                      # Dev server on http://localhost:5173
```

### 5. Access the Platform

Open your browser to `http://localhost:5173`.

- **Demo Account**: `demo@privateresume.local`
- **Password**: `Password123!`

---

## 🧭 Four Core Product Areas

| Product Area     | Path            | Key Capabilities                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :--------------- | :-------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Auth**         | `/auth`         | JWT bearer authentication, bcrypt password hashing, strict multi-tenant candidate data isolation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Profile**      | `/profile`      | Candidate Master Profile (personal details, skills, experience, projects, education, certifications) with inline Edit/Save CRUD + PyMuPDF & PyMuPDF4LLM layout-aware master resume parsing + Personal LaTeX Template Package Manager (`.tex` / `.zip`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **Workspace**    | `/` (Workflow)  | **5-Stage Progressive Tailoring Engine**:<br>1. **Job Intake**: Opportunity metadata capture, INR compensation formatting (`₹ 12,00,000`), and JD ingestion.<br>2. **JD Analysis**: Ollama structured requirements extraction with deterministic taxonomy fallback; sentence-level Required vs. Preferred skill categorization.<br>3. **Match Evidence**: 4-category deterministic skill classification & Estimated Match Score (0–100%).<br>4. **Tailoring Studio**: Line-by-line inline editing for every section and heading, "Ask AI to Polish" contextual refinements under anti-fabrication guards, and immutable version forking (`v1` $\to$ `v2`).<br>5. **PDF**: Instant compiled PDF document preview with PDF.js yellow hover links, sub-second pdflatex compilation, one-click authenticated download, candidate-approved tracking ("Log to Tracker"), and multi-cycle workspace isolation. |
| **Applications** | `/applications` | Pipeline tracking board (`saved`, `applied`, `assessment`, `interview`, `rejected`, `offer`, `withdrawn`), chronological interview notes, and direct download of the exact submitted PDF snapshot.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

---

## 📑 Custom LaTeX Template Engine

Candidates can upload their own preferred LaTeX resume designs in the Profile tab:

- **Supported Formats**: Single `.tex` files or `.zip` packages containing `.cls`, `.sty`, and font assets.
- **Universal AST Injection**: Intelligently identifies and populates candidate sections across `\begin{rSection}{...}`, `\cvsection{...}`, and standard `\section*{...}` blocks.
- **Offline Self-Contained Shims**: Automatically injects link (`\providecommand{\href}`) and layout shims to guarantee compilation without missing-package errors or network timeouts.
- **Instant Fallback**: Reverting to the built-in system default template takes a single click.

---

## 🧪 Testing & Verification Governance

PrivateResume maintains strict industry-grade layered testing governance with all results tracked in repository test workbooks:

```bash
# Run complete backend pytest suite (49 tests)
cd backend
pytest tests/ -v -m "not e2e"

# Run Playwright E2E browser tests
cd frontend
npx playwright test

# Build frontend production bundle
cd frontend
npm run build
```

---

## 🛡️ Security & Privacy Guardrails

- **Zero Telemetry**: No tracking scripts, analytics beacons, or remote cloud logging.
- **Secure Response Headers**: Enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, and strict CORS policies.
- **Controlled Subprocess Invocation**: LaTeX is compiled in isolated temporary workspaces with `-interaction=nonstopmode -halt-on-error -disable-installer -no-shell-escape` preventing arbitrary shell execution or network requests.
- **LaTeX Sanitization**: All user inputs undergo strict character escaping (`&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, `\`) before template interpolation.
- **Human In The Loop**: No automatic submissions or unsupervised AI generation.
