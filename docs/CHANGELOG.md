# PrivateResume - Changelog

All notable changes to the PrivateResume platform are documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/) and follows standard architectural change management.

---

## [1.0.0] - 2026-10-19

### Highlights
- Complete local-first, privacy-first AI-assisted resume tailoring platform.
- Zero external data leakage: React frontend communicates exclusively with FastAPI backend; PostgreSQL and Ollama AI execute locally.
- Strict anti-fabrication guarantee: Candidate profile serves as the immutable ground of truth; skills are never invented.

### Added
- **Authentication & Multi-Tenant Isolation (Epic 1)**:
  - User registration and login with Bcrypt password hashing.
  - Stateless JWT access token generation and validation.
  - Dependency-injected `get_current_active_user` enforcing row-level security across all queries.
- **Candidate Master Profile & PDF Ingestion (Epic 2)**:
  - PyMuPDF text and layout extractor parsing master resumes into structured profile entities.
  - Inline CRUD for Skills, Experience, Projects, Education, and Certifications.
  - Native `<input type="date">` calendar selectors for all historical milestones.
- **Job Intake Engine (Epic 3)**:
  - Multi-status job opportunity management (Active, Applied, Archived).
  - Opportunity compensation tracking with automated INR currency formatting (`₹ 12,00,000`).
- **Precision JD Analysis Engine (Epic 4 & Epic 14)**:
  - Dual-mode extraction engine: local Ollama (`mistral` model) JSON generation with a comprehensive deterministic taxonomy fallback.
  - Domain-specific coverage for Database Developers, Software Engineers, DevOps, Protocols, and Data Analysis.
  - Sentence-level classification into Required vs. Preferred skills based on keyword qualifiers (`prefer`, `exposure to`, `nice to have`).
  - Non-hallucinated experience extraction matching exact year ranges or defaulting strictly to `"Not specified"`.
- **Evidence-Grounded Resume Matching (Epic 5)**:
  - Deterministic 4-category evidence classification: Matched Skills, Weakly Represented, Missing Skills, and Unsupported Claims.
  - Estimated Job Match algorithm (0–100%) grounded purely in verified profile facts.
- **Stage 4 Progressive Tailoring Studio (Epic 6 & Epic 12)**:
  - Immutable version snapshots (`v1` $\to$ `v2` $\to$ `v3`) preserving historical audit integrity.
  - Granular, line-by-line inline editing and save capability for Headings, Professional Summary, Technical Competencies, Work History, and Key Projects.
  - "Ask AI to Polish" interactive refinement strictly bounded by candidate's profile context.
- **LaTeX Compilation & Custom Template Package Engine (Epic 7, 13 & 14)**:
  - Personal LaTeX Template Package Manager in Profile: supports custom `.tex` templates and `.zip` packages (including FAANGpath and modern CV classes) with fallback to default ATS template.
  - Intelligent AST/regex injection supporting `\begin{rSection}`, `\cvsection`, and standard LaTeX `\section` environments.
  - Hardened compilation pipeline using `pdflatex` with `-halt-on-error`, `-disable-installer`, and `-no-shell-escape` flags to eliminate network timeouts or interactive hangs.
  - Automatic self-contained link (`\providecommand{\href}`) and paragraph shims for 100% offline compilation resilience.
- **Clean Stage 5 PDF Workflow & Multi-Cycle Isolation (Epic 12 & 13)**:
  - Streamlined "5. PDF" viewer showing instant document preview without intrusive modal popups.
  - One-click authenticated PDF download that automatically registers the opportunity in the Applications pipeline.
  - Automatic workspace state reset upon download to guarantee a clean slate for subsequent job applications.
  - Header "New Job Intake" quick-reset control.
- **Application Tracking Dashboard (Epic 9)**:
  - Kanban-style application management supporting statuses: Saved, Applied, Assessment, Interview, Rejected, Offer, Withdrawn.
  - Linkage to the exact immutable tailored resume version submitted.
- **Quality Assurance & Testing (Epic 10 & 14)**:
  - 49 automated Pytest unit and integration tests passing with 100% success rate.
  - Vite production build pipeline verified (`npm run build`).
  - Security hardening middleware enforcing `X-Content-Type-Options: nosniff` and `X-Frame-Options: SAMEORIGIN`.

### Changed / Streamlined
- Removed the "Categorized Technical Stack" 5-box breakdown from Stage 2 per user feedback, leaving a cleaner, more focused requirements view.
- Removed audit health score and compiler terminal windows from Stage 5 to deliver a distraction-free, professional PDF view.
- Replaced manual compiler selection with automated background compilation.

### Security & Privacy Compliance
- Zero cloud telemetry.
- No resume content or PII dispatched to third-party endpoints.
- Isolated filesystem workspace per user compilation.
