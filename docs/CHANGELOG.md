# PrivateResume - Changelog

All notable changes to the PrivateResume platform are documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/) and follows standard architectural change management.

---

## [1.1.0] - 2026-10-23

### Highlights
- Standardized local Ollama model to `qwen3:4b-instruct` across JD analysis, hybrid profile parsing, and section refinement.
- Single Master Resume per candidate enforced at the database level via Alembic migration `011_enforce_single_master_resume_per_user`.
- Persisted atomic Profile Section Reset and Global Reset All (`DELETE /api/v1/profile/sections/{section}` and `/api/v1/profile/reset-all`) with complete form draft clearing across reloads and Master Resume PDF preservation.
- Full PDF.js interactive link preview with yellow hover highlights and dashed borders.
- Decoupled PDF download flow from application logging to uphold candidate agency.

### Added & Enhanced
- **Project Re-upload Deduplication & Deterministic JD Experience Parsing**:
  - Implemented `normalize_project_title` and `is_same_project_title` in `profile_service.py` using `difflib.SequenceMatcher >= 0.9` with badge text removal (`[GitHub]`, `[Live]`) and alphanumeric normalization.
  - Automatically deduplicates incoming projects within extracted lists and skips existing profile projects on re-upload unless explicit overwrite is enabled.
  - Added within-list deduplication to experience, education, and certifications.
  - Added deterministic parser `parse_jd_experience` in `ollama_provider.py` recognizing "0-2 years", "0 to 2 years", "0–2 yrs", "1-3 years", "2+ years", "at least 3 years", "minimum 5 years", and "fresher"/"entry level" (min 0). Overrides LLM values when patterns match.
  - Updated JD analysis prompt to request `min_years` and `max_years`.
  - Persisted `min_years` in existing DB column `experience_years` and `max_years` in JSON payload `raw_analysis` (0 database migrations).
  - Displayed full experience range in API and UI. Evaluated qualification in `matching_service.py` using `min_years` so candidates with 0 years match "0 to 2 years" requirements.
- **Layout-Aware Master Resume Extraction with PyMuPDF4LLM & Normalization (Epic 28)**:
  - Transitioned primary text extraction in `PdfService.extract_text_from_pdf` to `pymupdf4llm.to_markdown(file_path, write_images=False)`, delivering layout-aware block extraction that eliminates cross-column and coordinate-interleaving artifacts.
  - Implemented `clean_resume_markdown` pipeline that:
    - Normalizes `<br>` to `\n` to restore paragraph and bullet structure inside table-detected cells.
    - Strips HTML wrapper tags (`<u>`, `</u>`, etc.) without disturbing text.
    - Removes markdown table separators (`|---|`) and strips line-boundary pipes while preserving interior pipes (`|`) used in role titles and tech lists.
    - Strips markdown formatting (headers `#`, bold `**`, strikethrough `~~`, italics `*`/`_`, horizontal rules).
    - Normalizes non-standard bullet symbols (`[•●▪◦*\ufffd]`) to standard `- ` markers and joins hyphenated line breaks.
  - Retained legacy raw stream text extractor as `extract_text_from_pdf_plain` for regression comparison.
  - Preserved `extract_links_from_pdf` intact, extracting PyMuPDF native link annotations without regressions.
  - Updated `debug_extraction.py` in workspace root to print RAW, raw MARKDOWN, and CLEANED outputs along with character/line statistics and section key diffs.
  - Added `pymupdf4llm>=1.24.10,<2.0.0` to `backend/requirements.txt` maintaining strict compatibility with `PyMuPDF==1.28.2`.
- **Profile Reset Semantics (Persisted DB Deletion & Draft Clearing) (Epic 27)**:
  - Atomic database deletions via `DELETE /api/v1/profile/sections/{section}` and `DELETE /api/v1/profile/reset-all` (`profile_service.reset_section` and `reset_all`), deleting rows from `CandidateSkill`, `Project`, `Experience`, `Education`, and `Certification`, and clearing personal metadata fields to `None`.
  - Controlled neo-brutal confirmation modal in `ProfilePage.jsx` (`Reset & Delete` / `Reset All Sections`).
  - Clears form drafts, active edit states, resets badges to 0, and reloads authoritative state via `loadProfileAndResumes(false)`.
  - Master Resume PDF, job opportunities, applications, and tailored resumes remain untouched and preserved. User isolation enforced.
  - Verified with 3 backend integration tests in `test_profile_and_resume.py` and 4 Playwright E2E browser tests in `profile_reset_save.spec.js`.
- **Single Master Resume Enforcement & Notification Auto-Dismissal (Epic 26)**:
  - Enforced single active Master Resume per candidate across all layers: unique DB constraint `uq_master_resumes_user_id` on `master_resumes.user_id` via Alembic migration `011_enforce_single_master_resume_per_user`.
  - Backend upload API rejects additive second uploads with `400 Bad Request` unless `replace=true` is explicitly requested (`POST /api/v1/resumes?replace=true`).
  - Seamless in-place replacement workflow (`?replace=true`): updates existing master resume record in-place, deletes orphaned previous file from storage, triggers re-extraction without duplicating records.
  - Delete workflow allows candidate to delete existing resume and immediately reveals fresh "Upload Master PDF" trigger.
  - Green success notification auto-dismissal: all success banners in Profile and Applications automatically clear after 4 seconds with timer cleanup.
- **Master Resume Projects Extraction Pipeline Improvement (Epic 25)**:
  - State-aware sequential line parsing separates Project Title, Date Line, Tech Line, and Bullets across multiple lines without false project initialization.
  - Stripped link badges (`[Live]`, `[GitHub]`, `[Demo]`, etc.) from titles and prevented them from being categorized as technical skills.
  - Robust non-capturing group regex for date splitting, consecutive title boundary detection, and dual `github_url` and `live_url` association.
- **Targeted Master Resume Extraction & Hybrid Structuring (Epic 24)**:
  - Enhanced PyMuPDF parser to capture multi-role progressions at the same company, multi-line bullet continuations, and verification URLs.
  - Hybrid extraction pipeline integrating local Ollama (`qwen3:4b-instruct`) structuring methods invoked when section layout is ambiguous, backed by strict token grounding against source text and seamless deterministic fallback.
  - Polished `ReviewExtractionModal.jsx` removing redundant disclaimer banners.
- **Master Resume Integration & Ephemeral Resolution Engine (Epic 23)**:
  - Alembic migration `010_add_extracted_data_to_master_resumes.py` adding `extracted_data` JSON column to `master_resumes`.
  - Pre-generation `ResolutionService` enforcing strict precedence: 1) Tailored Resume, 2) Reviewed Candidate Profile, 3) Master Resume Extraction, 4) None. Resolution is ephemeral and does not mutate saved database records.
  - Added `ReviewExtractionModal.jsx` enabling candidates to inspect extracted items and selectively apply sections with comparison badges.
- **Runtime Remediation: Visible LinkedIn Header & Annotation Overlay (Epic 22)**:
  - Corrected LinkedIn header URL formatting and regex in `latex_service.py` and added `\def\linkedinurl{}` into LaTeX templates.
  - Integrated `pdfjs-dist@3.11.174` in frontend container with coordinate-exact yellow hover highlight overlays (`rgba(254, 240, 138, 0.75)`).
- **Header LinkedIn, 3-Line Education Layout & Certifications (Epic 21)**:
  - Placed clickable `\underline{LinkedIn}` directly beneath `\underline{GitHub}` in header contact block.
  - Enforced 3-line Education layout (Degree & dates, Institution, CGPA/GPA).
  - Formatted Certifications as `Certificate Name --- Provider --- [Certificate]`.
- **Dedicated Project Dates, Right-Aligned Dates & Certificate Links (Epic 20)**:
  - Added `start_date`, `end_date`, and `is_current` to project models, tailoring schemas, and UI.
  - Formatted Experience and Project dates to right-align at `576.0 pt` margin using LaTeX `\hfill`.
  - Added `certificate_url` field rendering clickable `[Certificate]` links.
- **Exclusive SWE Default LaTeX Template & 6-Section Dynamic Ordering (Epic 19)**:
  - Adopted SWE resume template ZIP (`media_1792600889842_f4354a6c.zip`) with Source Sans Pro typography, centered headline, and 1pt header rule.
  - Strict 6-section order enforced: Summary $\to$ Education $\to$ Skills $\to$ Experience $\to$ Projects $\to$ Certifications & Achievements.
  - Stripped duplicate bullets and guaranteed 100% vector Type 1 fonts.
- **Single Fixed Default Template Adoption (Epic 18)**:
  - Established `backend/app/templates/default` as the single canonical template directory, removing obsolete alternate directories.
- **Custom LaTeX Template Integration & Layout Enforcement (Epic 17)**:
  - Replaced regex replacement strings in `_inject_into_custom_template` with callable `lambda m:` functions to safely handle LaTeX commands and backslashes without Python escape errors.
- **Containerized Environment Dynamic Vite Proxy Configuration (Epic 16)**:
  - Updated `frontend/vite.config.js` to detect Docker environments (`/.dockerenv`) or respect `VITE_BACKEND_TARGET`, routing API traffic directly to internal container services.
- **LaTeX Security Hardening & Candidate Agency Decoupling (Epic 15)**:
  - Authenticated Applications download links with Bearer token authentication and blob URL revocation.
  - Decoupled PDF downloading from application logging: added explicit "Log to Tracker" candidate action, removing premature workspace wiping.
  - Hardened `ValidationService` against placeholder leakage and sanitized PDF health check exceptions.
  - Added comprehensive ZIP path traversal, symlink, and file count limits in `test_latex_template_security.py`.

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
