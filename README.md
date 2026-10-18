# PrivateResume

> **Privacy-First, Local-First AI-Powered Resume Tailoring & Application Platform**

PrivateResume empowers job seekers to analyze job descriptions, align real candidate evidence deterministically, progressively tailor high-density resumes, compile ATS-compliant PDFs via local LaTeX, validate machine-readability through objective ATS quality gates, and track the entire opportunity lifecycle — **with zero data leakage, zero hallucinations, and zero external telemetry**.

---

## 🏛️ Core Principles & Constitutional Rules

1. **AI Recommends · Candidate Approves · System Generates**: The candidate retains absolute veto and editorial control over every bullet, section, and claim.
2. **Strict Anti-Fabrication Guarantee**: Missing skills are honest gaps, never instructions to invent experience. Resume tailoring only highlights and re-orders verifiable candidate achievements.
3. **Version Immutability**: Historical resume versions (`v1`, `v2`, `v3`) are permanent, immutable snapshots. Modifying a finalized draft forks a new version to preserve submission history.
4. **Local-First & Private by Default**: Resume PDFs, SQLite/PostgreSQL records, and local Ollama inference remain on your machine. No third-party LLM APIs receive your sensitive career history.
5. **Deterministic ATS Compliance**: No fancy multi-column graphics or non-standard tables that confuse applicant tracking systems. Output is compiled through robust LaTeX typography primitives into selectable, machine-parsable PDF streams.

---

## 🛠️ Architecture & Tech Stack

```text
React 18 + Vite (Tailwind CSS Neo-Brutalist UI)
       │
       ▼ (REST API / Bearer JWT)
FastAPI Modular Monolith (Python 3.11+)
  ├── Core Security & Middleware (X-Frame-Options: SAMEORIGIN, CORS lockdown)
  ├── PyMuPDF Engine (Text extraction & ATS extractability audit)
  ├── Local Ollama Provider (Mistral / Llama 3 with deterministic fallbacks)
  ├── Deterministic Match & Scoring Engine (0-100% Estimated Job Match)
  ├── Subprocess LaTeX Compiler (pdflatex -no-shell-escape)
  └── PostgreSQL 15+ & SQLAlchemy ORM (Alembic Migrations 001 - 009)
```

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React icons.
- **Backend**: FastAPI, Pydantic V2, SQLAlchemy 2, Alembic, PyMuPDF.
- **Database**: PostgreSQL (containerized or local) with indexed relational foreign keys.
- **Inference**: Ollama (native host or container gateway).
- **Typesetting**: Native `pdflatex` (MiKTeX on Windows / TeX Live on Linux).
- **Testing**: Pytest (48 automated tests), Playwright (E2E browser tests), GitHub Actions CI.

---

## 🚀 Quick Start

### Option A: Local Native Development (Recommended for fast iteration)

#### 1. Start PostgreSQL
```bash
docker run -d --name privateresume-db -e POSTGRES_DB=private_resume -e POSTGRES_USER=private_resume_user -e POSTGRES_PASSWORD=private_resume_password -p 5433:5432 postgres:15-alpine
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows (or source venv/bin/activate on Unix)
pip install -r requirements.txt
alembic upgrade head             # Runs migrations 001 through 009
python seed.py                   # Seeds demo account (Alex Morgan)
uvicorn app.main:app --port 8005 --reload
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev                      # Dev server on http://localhost:5173
```

#### 4. Open Application
Navigate to `http://localhost:5173`.
- **Demo Account**: `demo@privateresume.local`
- **Password**: `Password123!`

---

### Option B: Multi-Container Docker Stack
```bash
docker compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend API & Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 🧭 Four Core Product Areas

| Product Area | Path | Key Capabilities |
|---|---|---|
| **Auth** | `/auth` | JWT bearer authentication, bcrypt password hashing, strict multi-tenant candidate data isolation. |
| **Profile** | `/profile` | Candidate Master Profile (personal details, skills, experience, projects, education, certifications) + PyMuPDF local master resume parsing. |
| **Workspace** | `/` (Workflow) | **5-Stage Progressive Tailoring Engine**:<br>1. **Job Intake**: Raw job description ingestion and metadata capture.<br>2. **JD Analysis**: Ollama structured requirements extraction with deterministic fallback.<br>3. **Match Evidence**: 4-category deterministic skill classification & Estimated Match Score (0-100%).<br>4. **Tailor & AI Edit**: Section editing, "Ask AI" contextual refinements under anti-fabrication guards, and version forking.<br>5. **Validate & PDF**: Subprocess LaTeX PDF compilation, inline PDF preview, and 6-point ATS Pre-Flight Quality Gate. |
| **Applications** | `/applications` | Pipeline tracking dashboard (`draft`, `applied`, `interviewing`, `offer`, `rejected`, `archived`), chronological interview notes, and direct download of the exact submitted PDF snapshot. |

---

## 🧪 Testing & Verification Governance

PrivateResume maintains strict industry-grade layered testing governance with all results tracked in repository test workbooks:

### Automated Test Suite
```bash
# Run complete backend pytest suite (48 tests)
cd backend
pytest tests/ -v

# Run Playwright E2E browser tests (Chromium)
cd frontend
npx playwright test
```

### Verified QA Workbooks
- [`docs/PrivateResume_Automation_Test_Cases.xlsx`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/PrivateResume_Automation_Test_Cases.xlsx): 53 automated test cases logged and verified.
- [`docs/PrivateResume_Manual_Test_Cases.xlsx`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/docs/PrivateResume_Manual_Test_Cases.xlsx): 25 manual test cases verified across all modules.

---

## 🛡️ Security & Privacy Guardrails

- **Zero Telemetry**: No tracking scripts, analytics beacons, or remote cloud logging.
- **Secure Response Headers**: Enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, and strict CORS policies.
- **Controlled Subprocess Invocation**: LaTeX is compiled in isolated temporary workspaces with `-interaction=nonstopmode -no-shell-escape` preventing arbitrary shell execution or network requests.
- **LaTeX Sanitization**: All user inputs undergo strict character escaping (`&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, `\`) before template interpolation.
- **Human In The Loop**: No automatic submissions or unsupervised AI generation.

---

## 📄 License
PrivateResume is proprietary software developed locally for private candidate use.
