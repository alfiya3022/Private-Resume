# PrivateResume - Current Project State

## Project phase
Epic 29 — Local LLM-First Master Resume Ingestion, Whole-Document Extraction & Categorized Skill Pipeline Complete. All Project Epics (0 through 29) Complete & Verified.

## Current status
- **Epic 0 — Foundation**: Git repo, React Vite Tailwind frontend, FastAPI modular monolith, PostgreSQL, Docker Compose, root documentation.
- **Epic 1 — Auth & User Isolation**: Bcrypt passwords, JWT bearer tokens, user registration/login, user isolation middleware.
- **Epic 2 — Master Profile & PDF Ingestion**: PyMuPDF extraction, candidate profile CRUD (personal, skills, experience, projects, education, certifications), file upload storage.
- **Epic 3 — Job Intake Engine**: Job entity, status lifecycle, Workspace Stage 1 intake selector and saved job manager.
- **Epic 4 — Structured JD Analysis**: Local Ollama extraction with deterministic fallback, categorized requirements.
- **Epic 5 — Resume-to-Job Matching**: Deterministic 4-category classification, Estimated Job Match (0-100%), evidence citations, anti-fabrication rules.
- **Epic 6 — Tailoring & Human Editing**: `TailoredResume` model with version immutability (`v1` $\to$ `v2` $\to$ `v3`), Ask AI section refinement under anti-fabrication constraints, Workspace Stage 4 editor.
- **Epic 7 — LaTeX + PDF Generation**: Controlled LaTeX escaping engine, clean ATS LaTeX template, isolated subprocess compilation, `ResumeArtifact` persistence, inline document streaming.
- **Epic 8 — Resume Validation Engine**: ATS pre-flight engine (`ValidationService`) evaluating 6 objective checks (PDF health, text extractability, contact info, headings, placeholders, evidence grounding), interactive Stage 5 Quality Gate panel.
- **Epic 9 — Application Tracking Engine & Dashboard**: `Application` relational model, Alembic migration 009, dedicated `/applications` pipeline dashboard with status filtering and interview notes, 1-click Workspace Stage 5 logging.
- **Epic 10 — Testing, CI Pipeline & Security Hardening**: GitHub Actions CI workflow (`.github/workflows/ci.yml`), `SecurityHeadersMiddleware` (X-Content-Type-Options, X-Frame-Options: SAMEORIGIN), Playwright E2E browser test suite.
- **Epic 11 — Final Polish, Documentation & Packaging**: Production multi-container Docker Compose configuration, idempotent database seed utility (`backend/seed.py`), sleek clutter-free neo-brutalist UI polish, and comprehensive production README documentation.
- **Epic 12 — User Experience Polish & Stage 4/5 Refinements**:
  - Full inline Edit & Save CRUD for Projects and Experience in Profile tab.
  - Native `<input type="date">` calendar selectors for all historical dates.
  - LaTeX Template Package Manager accepting `.zip` packages only, with compiler line removed.
  - INR currency auto-formatting (`₹ 12,00,000`) for Opportunity compensation.
  - Anti-hallucination JD experience extraction defaulting strictly to "Not specified" if unspecified.
  - Stage 4 Progressive Tailoring Studio with full CRUD & inline Save buttons for every line (Resume Heading, Summary, Skills categories/items, Experience roles/bullets, Projects/bullets, Education & Certifications).
  - Stage 5 clean "5. PDF" generation tab with audit health panel removed, MiKTeX compiler banner removed, terminal/black window removed, re-compile option removed, and reliable authenticated PDF download with automatic logging into the Applications tracker.
- **Epic 13 — Template Engine Personalization, Multi-Cycle Isolation & Clean Flow**:
  - Candidate-provided LaTeX template engine: Automatically renders resumes using candidate's uploaded `.tex` or `.zip` template; cleanly falls back to system base template when removed.
  - Education & Certification inline CRUD: Added full inline Edit and Save functionality to Education and Certification cards in Candidate Profile.
  - Seamless Stage 4 to Stage 5 transition: Eliminated direct download/audit modal popups upon clicking "Proceed to Stage 5: PDF", rendering the PDF preview directly in the viewer.
  - Clean workspace multi-cycle isolation: Downloading a PDF auto-logs the opportunity to the Applications pipeline and fully wipes active workspace draft state so prior content never spills over into subsequent applications.
- **Epic 14 — Compilation Hardening, Comprehensive JD Extraction & UI Streamlining**:
  - LaTeX Compilation Resilience: Resolved pdflatex process hangs by adding `-halt-on-error` and `-disable-installer` flags, and injecting self-contained shims for `hyperref` and `parskip` packages to eliminate network CTAN calls and interactive prompts.
  - Custom Template Compatibility: Added native regex support for `\begin{rSection}` environments (FAANGpath and modern CV templates) in `_inject_into_custom_template` so custom uploaded templates receive tailored content seamlessly.
  - UI Simplification: Completely removed the "Categorized Technical Stack" section from Stage 2 (Job Requirements Analysis) per user request.
  - Precision JD Scraping: Vastly expanded tech taxonomy for database roles, administration, protocols, data querying, and scripting; added intelligent sentence-level required vs. preferred classification and accurate experience-year parsing.

- **Epic 15 — LaTeX + PDF Security Hardening & Correctness Remediation**:
  - Authenticated Applications Downloads: Replaced raw unauthenticated `<a>` download links in Applications tracker (`ApplicationsPage.jsx`) with Bearer token authentication via `api.getToken()`, checking HTTP response status and revoking object URLs safely.
  - Decoupled PDF Downloads & Candidate Agency: Removed implicit application creation and premature workspace wiping from `handleDownloadPdf` in `WorkspacePage.jsx`. Added an explicit "Log to Tracker" candidate action alongside "Download PDF", upholding the product principle that the candidate reviews and approves before logging.
  - Validation Engine Hardening: Expanded `ValidationService` placeholder detection to cover template syntax (`{{...}}`, `<<...>>`), bracketed placeholders (`[Company Name]`, `[Insert ...]`), and draft markers (`TODO`, `TBD`, etc.). Sanitized PDF health inspection exception handling to prevent leaking server filesystem paths.
  - LaTeX Security Regression Suite: Added comprehensive regression tests in `test_latex_template_security.py` verifying ZIP path traversal rejection, maximum archive file count limit (100 files), symlink rejection, absolute path rejection, and server-side compilation error sanitization. All 62 backend tests passing.

- **Epic 16 — Containerized Environment PDF Preview & Download Resolution**:
  - Root Cause Diagnosed: Frontend Vite dev server proxy target was statically configured to `http://127.0.0.1:8005`. Inside the frontend Docker container, nothing listened on port 8005, causing Vite to fail with `connect ECONNREFUSED 127.0.0.1:8005` (surfaced to the browser as HTTP 500 when requesting `/api/v1/tailored-resumes/:id/pdf`).
  - Dynamic Proxy Configuration: Enhanced `frontend/vite.config.js` to detect Docker environment (`/.dockerenv`) or respect `VITE_BACKEND_TARGET`, proxying `/api` directly to internal Docker service `http://backend:8000` inside containers, and `http://localhost:8000` when running locally outside Docker.
  - Verified Functionality: Authenticated PDF download and preview requests through `http://localhost:5174/api/v1/tailored-resumes/4/pdf` return HTTP 200 with `application/pdf` and valid `%PDF-` payload (78,115 bytes). All 15 PDF generation & template security tests passing.

- **Epic 17 — Custom LaTeX Template Integration & Layout Enforcement**:
  - Root Cause Diagnosed: During custom template rendering (`FAANGPath_Simple_Template.zip`), `_inject_into_custom_template` called `re.sub(pattern, repl, text)` with string `repl` arguments containing LaTeX backslashes (`\cdot`, `\textbf`, etc.). Python 3.12 raised `re.error: bad escape \c`, which was silently caught by `render_latex`'s fallback handler, causing the system to silently revert to `default_resume.tex`.
  - Targeted Solution: Replaced all regex replacement strings in `_inject_into_custom_template` with callable `lambda m:` functions, ensuring LaTeX commands and backslashes in candidate content are treated as literal text.
  - Template Layout & Data Cleanliness: Injected candidate's verified contact info (`\address` phone, location, email, GitHub, LinkedIn), tailored content into `\begin{rSection}` environments (Summary, Education, Skills, Experience, Projects, Certifications), and automatically removed unpopulated template sample sections (e.g. sample Leadership, Achievements) to uphold anti-fabrication principles.
  - Live Verification: Generated live PDF for tailored resume 4 (`/app/storage/artifacts/2/resume_v1_job3.pdf`). Confirmed with PyMuPDF text extraction that the FAANGPath layout (`resume.cls` with uppercase header, diamond address separator, horizontal rules) is applied with candidate's actual tailored data and zero dummy text. All 16 backend PDF generation and template security tests passing.

- **Epic 18 — Single Fixed Default LaTeX Template Adoption (`data_science_tech_resume_template`)**:
  - Single Default Template Architecture: Adopted the original LaTeX source files from `data_science_tech_resume_template(2).zip` (`resume.tex`, `_header.tex`, `TLCresume.sty`, `sections/*.tex`, `LICENSE.txt`, `README.md`) as the single, fixed default resume template in `backend/app/templates/default`. Removed obsolete alternate template directories (`backend/app/templates/builtin`).
  - Styling & Visual Fidelity: Preserved exact original styling—Source Sans Pro font family (`sourcesanspro`), font sizes, weights, margins (0.5in sides, 0.5in top, 1in bottom), header rule, highlight blue (`RGB(61, 90, 128)`), section formatting with `\scshape`, `zitemize` compact item spacing, and tabular skills layout. Added `texlive-fonts-extra` to `backend/Dockerfile` so native Type 1 font binaries compile with zero warnings or missing font fallbacks.
  - Robust Candidate Data Mapping: Parameterized LaTeX macros and sections dynamically with candidate's actual verified contact info, target role, summary/objective, skills categories, professional experiences and technical projects, education degrees, and activities/certifications with full LaTeX-special character escaping.
  - Graceful Optional Field Handling: Parameterized `_header.tex` with clean TeX conditionals (`\ifx\field\empty\else ... \fi`) so missing optional fields (portfolio, GitHub, LinkedIn, phone, city) are cleanly omitted without generating broken links or blank lines.
  - Verification & Sign-Off: All 21 backend tests in `test_pdf_generation.py`, `test_latex_template_security.py`, and `test_validation.py` passing with 100% success. Generated live candidate resume (`resume_v1_job3.pdf`) matching the reference template page geometry (612x792 pt Letter), exact `0x3d5a80` highlight blue color, and zero sample text. Frontend production build passing with 0 errors (`npm run build`).

- **Epic 19 — SWE Resume ZIP Default LaTeX Template Integration & 6-Section Dynamic Ordering**:
  - Exclusive SWE Default Template: Integrated the SWE resume template ZIP (`media_1792600889842_f4354a6c.zip`) as the exclusive default LaTeX template in `backend/app/templates/default`. Features 9pt Source Sans Pro typography, 0.5in side and top margins, 1.0in bottom margin, left-aligned contact block (`\city`, `\phone`, `\email`, `\underline{GitHub}`, `\underline{LinkedIn}`), centered name with portfolio link and target headline in `#3D5A80` highlight blue, 1pt header rule, and 6 modular section files in `sections/`.
  - Strict 6-Section Dynamic Ordering: Enforced the exact 6-section order across both the PDF generation pipeline (`latex_service.py`) and the Stage 4 Tailoring Studio (`WorkspacePage.jsx`):
    1. `SUMMARY` (Objective / Professional Summary)
    2. `EDUCATION` (Degree, Year, Institution, CGPA / GPA)
    3. `SKILLS` (Bold category, colon, comma-separated skill list)
    4. `EXPERIENCE` (Company, dates, role, location, single-marker bullet points)
    5. `PROJECTS` (Project title, active clickable `[Live]` / `[GitHub]` links, tech stack in italics, clean bullets)
    6. `CERTIFICATIONS & ACHIEVEMENTS` (Bullet points with certification title, issuer, date)
  - Elimination of Visual & Formatting Defects:
    - Stripped duplicate bullet characters (`• •`, `-`, `*`) in bullet lists before injecting into LaTeX `\item`.
    - Formatted Education records into discrete subheading blocks with degree, graduation years, institution, and CGPA/GPA without concatenated text.
    - Preserved native `hyperref` compilation in Docker pdflatex, generating real PDF link annotations (`/Subtype /Link`) with zero dummy shims.
    - Zero Type 3 fonts: 100% vector Type 1 Source Sans Pro font embedding.
  - Live API & Document Verification: Compiled live candidate resume 4 via HTTP API (`POST /api/v1/tailored-resumes/4/generate-pdf`). Inspected resulting PDF (`167,724 bytes`, 1 page, `612.0 x 792.0 pt`) using PyMuPDF. Confirmed 0 Type 3 fonts, 4 active `/Subtype /Link` interactive URI annotations, clean text extraction of candidate name ("Alfiya Shaikh"), and flawless 6-section order. All 21 backend unit/security/validation tests pass with 100% success. Frontend builds cleanly (`npm run build`).

- **Epic 20 — Project Dates, Right-Aligned Date Layout, Certificate Links & Hyperlink Audit**:
  - Link Hover Behavior & Specification Audit: Dissected PDF annotations at xref level in user reference and generated PDFs. Both output identical ISO 32000-1 link annotations (`/Subtype /Link`, `/Border [ 0 0 0 ]`, `/H /I`, `/C [ 0 1 1 ]`). Verified that yellow hover highlights originate in client-side viewer CSS (specifically Mozilla's `pdf.js` annotation layer in Overleaf/web viewers) rather than static PDF bytecode. In Chromium's native PDFium iframe plugin, links trigger pointer cursor and browser status bar URL preview.
  - Dedicated Project Date Fields: Added `start_date`, `end_date`, and `is_current` (Ongoing) support to `ResumeProjectItem` Pydantic schema, `tailoring_service`, and Stage 4 Tailoring Studio (`WorkspacePage.jsx`). Added discrete inputs for Start Date/Year, End Date/Year, and Ongoing checkbox alongside dual `github_url` and `live_url` support.
  - Right-Aligned Dates: Formatted all Experience and Project dates to right-align at the right margin (`576.0 pt`) on the exact same line as the title using LaTeX `\hfill` without manual positioning or text collisions.
  - Certificate Link Field: Replaced certification date input in Stage 4 UI with an optional `certificate_url` field (`https://...`). In LaTeX generation, renders clickable `[Certificate]` links (`\href{<url>}{\textbf{ [Certificate]}}`) beside certification names while preserving historical date fields in the database without rendering dates in place of links in the PDF.
  - Verification & Full Regression Pass: Live API update and compile verified on candidate resume (`candidate_resume23.pdf`, 1 page, `612.0 x 792.0 pt`). PyMuPDF confirmed exact right-margin date alignments (`576.0 pt`), 6 active interactive `/Subtype /Link` annotations, and zero Type 3 fonts. Added automated regression test `test_project_dates_and_certificate_links_rendering` in `test_pdf_generation.py`; all 22 backend tests pass with 100% success. Frontend builds cleanly (`npm run build`).

- **Epic 21 — Header LinkedIn Integration, 3-Line Education Layout, Formatted Certifications & PDF.js Yellow Link Hover Preview**:
  - Header LinkedIn Placement: Placed clickable `\underline{LinkedIn}` directly beneath `\underline{GitHub}` in the left contact block of `_header.tex`. Clean username sanitization handles full LinkedIn URLs or bare usernames, escapes LaTeX special characters, and never exposes raw URLs in document text.
  - 3-Line Education Layout: Refactored `_build_education_code` in `latex_service.py` to format education entries into 3 discrete lines: Line 1: Degree name on left, dates right-aligned (`\hfill`); Line 2: College/institution name on its own line; Line 3: CGPA/academic details on its own line. Verified full editability and storage in both Candidate Profile and Workspace Stage 4.
  - Certifications & Achievements Presentation: Refactored `_build_certifications_code` to format entries as `Certificate Name --- Provider --- \href{<url>}{\underline{Certificate}}`, where only `Certificate` is underlined and linked, with raw URLs and generic labels eliminated, and link omitted when no URL is provided.
  - PDF.js In-App Preview with Yellow Hover Highlighting: Replaced standard browser `<iframe>` preview in `WorkspacePage.jsx` with a custom `PdfPreviewer.jsx` component powered by `pdfjs-dist@3.11.174`. Renders PDF pages on canvas with an interactive DOM annotation layer. Links trigger neo-brutal yellow hover highlighting (`rgba(254, 240, 138, 0.45)`) and dashed borders, while preserving link destinations, zoom controls, responsive scrolling, and download/generation flows.
  - Layered Testing & Verification: Added automated regression test `test_linkedin_header_and_education_three_line_layout` in `tests/test_pdf_generation.py`. All 23 backend tests pass with 100% success. Frontend production bundle cleanly built (`npm run build`) in 11.18s.

- **Epic 22 — Runtime Remediation: Visible LinkedIn Header & PDF.js Interactive Yellow Link Hover**:
  - Bug 1 (LinkedIn Header Visibility) Root Cause & Fix: Candidate profile had `https://www.linkedin.com/feed/` which was wiped to empty by an overly aggressive regex in `latex_service.py`, causing `\ifx\LinkedIn\empty` to suppress the header. Replaced regex with robust URL parsing, added `\def\linkedinurl{}` into `backend/app/templates/default/resume.tex`, refactored `_header.tex` to render `\href{\linkedinurl}{\underline{LinkedIn}}` directly below GitHub, and updated database profile. PyMuPDF verified live PDF output contains `LinkedIn` at `y = 67.4-81.4` right below `GitHub` (`y = 56.9-68.0`) linking to `https://www.linkedin.com/in/alfiya-shaikh1106`.
  - Bug 2 (Yellow Hover Highlight) Root Cause & Fix:
    1. Container dependency desync: `pdfjs-dist` was installed on the Windows host but not inside `privateresume_frontend` Docker container. Installed `pdfjs-dist@3.11.174` in the container.
    2. API incompatibility: `pdfjs-dist@3.x` does not provide static `AnnotationLayer.render`. Refactored `PdfPreviewer.jsx` to instantiate `new pdfjsLib.AnnotationLayer(...)` and call instance `.render()`.
    3. Worker blob restriction: Fetching `blob:` URLs inside web workers failed in browser; resolved by fetching `ArrayBuffer` in main thread and passing `data: new Uint8Array(buffer)` to `getDocument`.
    4. Link styling & overlay: Rendered coordinate-exact `.pdf-interactive-link-overlay` elements styled with yellow neo-brutal hover `#FEF08A` (`rgba(254, 240, 138, 0.75)`) and dashed borders.
  - Verification & Playwright E2E: Executed Playwright test `frontend/e2e/pdf_preview_hover.spec.js` against running app on `http://localhost:5174`. Verified 6 active link overlays detected, hovered over LinkedIn link, verified computed style `rgba(254, 240, 138, 0.75)`, and captured screenshot `pdf_preview_hover_verification.png`. All 23 backend tests in `pytest` passing.

- **Epic 23 — Master Resume Integration & Profile Feature Foundation**:
  - Database Migration & Storage: Created Alembic migration `010_add_extracted_data_to_master_resumes.py`, adding `extracted_data = Column(JSON, nullable=True)` to `master_resumes`. Preserves full structured extraction on the persistent `MasterResume` model instance.
  - Deterministic Extraction Engine (`pdf_service.py`): Implemented `extract_full_resume_data` using PyMuPDF to parse personal/contact info (phone, email, location, LinkedIn URL, GitHub URL, portfolio URL), skills, education (degree, institution, grades, dates), experience (company, title, location, dates, bullets), projects (title, tech, bullets, repository/live links, dates), and certifications (name, issuer, credential links) with clickable link annotation extraction.
  - Candidate Review & Agency Protection: Extracted data does NOT silently overwrite reviewed Profile data. Built comparison diff engine (`compare_extracted_data_with_profile`) and selective approval workflow (`apply_extracted_data_to_profile`). Added `ReviewExtractionModal.jsx` and "Review Extraction" button on master resume cards, allowing candidates to inspect extracted data, view comparison badges (New Value, Different/Conflict, Matches Profile), choose sections to apply, and toggle safe merging (`overwrite_existing=false` by default).
  - Safe Pre-Generation Missing-Information Recovery: Created `ResolutionService` (`backend/app/services/resolution_service.py`) enforcing the strict source precedence: 1) Tailored Resume, 2) Reviewed CandidateProfile, 3) Master Resume Extraction, 4) None. Resolution is ephemeral, does not mutate saved database records, enriches only included items with missing metadata (LinkedIn, GitHub, repository links, credential URLs, dates), and strictly prohibits restoring intentionally cleared fields, excluded projects, or omitted bullet points.
  - LaTeX + PDF & Validation Integration: Wired `resolution_service.resolve_effective_content` into `latex_service.py` (`generate_resume_artifacts`) and `validation_service.py`. The SWE template formatting, 6-section order, PDF link annotations, and PDF.js yellow link hover behavior remain 100% stable. Provenance tracking is surfaced to the candidate via an informative non-intrusive banner in Stage 5.
  - Automated & Layered Testing: Created `tests/test_master_resume_integration.py` covering extraction, upload diff, selective application, agency preservation, and recovery precedence. All 70 backend unit and integration tests passing in `pytest`. All 3 frontend E2E browser tests passing in Playwright. Test case workbooks (`PrivateResume_Automation_Test_Cases.xlsx` and `PrivateResume_Manual_Test_Cases.xlsx`) updated with executed results.

- **Epic 24 — Targeted Master Resume Extraction Improvement & Clean Review UI**:
  - Work Experience Extraction: Enhanced deterministic parsing in `pdf_service.py` to seamlessly capture multiple roles at the same organization (promotions or transfers), wrapped multi-line bullet continuations without losing bullets, location parsing, and `is_current` active role flags.
  - Projects Extraction: Enhanced project parsing with technology stack extraction from brackets, parentheses, pipes, or dedicated stack labels; full multi-line bullet and description preservation; start and end dates; and spatial/keyword link mapping with single-assignment tracking to completely prevent repo/demo link leakage across different projects.
  - Certifications Extraction: Enhanced certification parsing to extract certification name, issuer/organization, issue dates, credential IDs, and verification URLs without confusion with general skills or courses.
  - Hybrid Extraction Pipeline: Integrated local Ollama structuring methods (`structure_experience_section`, `structure_projects_section`, `structure_certifications_section`) in `ollama_provider.py` invoked conditionally when section layout is ambiguous or incomplete (`_is_experience_ambiguous`, `_is_projects_ambiguous`, `_is_certifications_ambiguous`).
  - Strict Source Grounding: Built strict token-level validators (`validate_and_ground_experience`, `validate_and_ground_projects`, `validate_and_ground_certifications`) that verify extracted entities against raw section text and document links, discarding any hallucinated companies, ungrounded bullets, or fake URLs. Seamless deterministic fallback guarantees zero downtime and zero failures if Ollama is offline or times out.
  - Review Modal Polish: Removed the "Candidate agency protected" amber banner from `ReviewExtractionModal.jsx` per user specification, maintaining full agency safeguards in the backend without redundant UI disclaimer text.
  - Layered Testing & Verification: Added comprehensive unit and integration tests in `backend/tests/test_master_resume_integration.py`. All 75 backend tests passing in `pytest` (100% success). All 3 frontend E2E browser tests passing in Playwright. Frontend production bundle verified with 0 errors (`npm run build`).

- **Epic 25 — Master Resume Projects Extraction Pipeline Improvement (Tab 1)**:
  - Multi-Line Project Header Desynchronization Fix: State-aware sequential line parsing separates Project Title, Date Line, Tech Line, and Bullets across multiple lines without false project initialization.
  - Link Badge Stripping: Cleaned link badges (`[Live]`, `[GitHub]`, `[Demo]`, `[Code]`, `[Website]`, `(Live)`, `(Demo)`) from project titles while ensuring badges are never falsely treated as technical skills.
  - Date Range Splitting Resilience: Replaced flawed character-class regex with non-capturing group `(?:\s*(?:[\-–—/]+|\bto\b)\s*)`, preventing `to` character class corruption where "Present" was truncated to "Presen".
  - Consecutive Boundary Identification: Added lookahead and structural signal detection to identify project titles lacking pipe or bracket characters (e.g. `Private Resume — AI-Powered Resume Application` and `Deep Learning-Based Image Fusion`) without absorbing them into preceding bullets.
  - Standalone Technology List Recognition: Correctly identifies comma-separated technical skills on standalone lines without requiring explicit `Technologies:` prefixes, distinguishing them from action-verb bullet sentences.
  - Accurate Dual Link Association: Supported extraction of both `github_url` and `live_url` per project without premature loop breaks, preserving strict single-assignment tracking to prevent link leakage across projects.
  - Real-World Fixture Verification: Validated on `SWE(2).pdf`, successfully extracting all 3 projects with exact titles, dates, technologies, bullets, and the `https://firsthomefintech.ae` live URL.
  - Automated & Layered Testing: Added `test_extract_projects_from_swe2_pdf_fixture` and `test_extract_projects_multiline_and_badge_resilience` in `test_master_resume_integration.py`. All 77 backend tests passing in `pytest` (100% success). All 3 Playwright E2E browser tests passing. Frontend production bundle cleanly built with Vite (`npm run build`).

- **Epic 26 — Single Master Resume PDF Enforcement & Profile Form Reset Baseline**:
  - Enforced single active Master Resume per candidate across all layers: unique DB constraint `uq_master_resumes_user_id` on `master_resumes.user_id` via Alembic migration `011_enforce_single_master_resume_per_user`.
  - Backend upload API rejects additive second uploads with `400 Bad Request` unless `replace=true` is explicitly requested (`POST /api/v1/resumes?replace=true`).
  - Seamless in-place replacement workflow (`?replace=true`): updates existing master resume record in-place, deletes orphaned previous file from storage, triggers re-extraction without duplicating records.
  - Delete workflow: allows candidate to delete existing resume and immediately reveals fresh "Upload Master PDF" trigger.
  - Profile UI dynamically conditionally renders either the single upload dropzone or the active resume control card (`Review Extraction`, `Replace PDF`, `Delete` trash button) preventing duplicate master resume records.
  - Green success notification auto-dismissal: all success banners in Profile and Applications automatically clear after 4 seconds with timer cleanup and reset on state changes; error notifications and modal validation dialogs remain visible indefinitely until user action.
  - Immediate Form Clearing: Refactored `handleTabReset` and `handleResetAll` in `ProfilePage.jsx` to immediately and visibly reset active editable controls upon clicking Reset, establishing a consistent active-entry form clearing baseline.

- **Epic 27 — Profile Reset Semantics (Persisted DB Deletion & Draft Clearing)**:
  - Database & Service Architecture: Added `reset_section(db, user_id, section)` and `reset_all(db, user_id)` in `backend/app/services/profile_service.py`. Deletions atomically query and delete rows from `CandidateSkill`, `Project`, `Experience`, `Education`, and `Certification` filtered strictly by `profile_id == profile.id`, and reset personal info fields (`headline`, `summary`, `phone`, `location`, `linkedin_url`, `github_url`, `portfolio_url`) to `None`.
  - RESTful API Endpoints: Added `DELETE /api/v1/profile/sections/{section}` and `DELETE /api/v1/profile/reset-all` in `backend/app/api/v1/endpoints/profile.py`, along with collection aliases (`DELETE /skills`, `DELETE /projects`, etc.), executing atomic transactions and returning the fresh `ProfileResponse`.
  - Frontend Reset Controls & Confirmation UX: Updated `handleTabReset` and `handleResetAll` in `ProfilePage.jsx` to prompt an intentional neo-brutal confirmation modal (`Reset & Delete` / `Reset All Sections`). Upon confirmation, calls `profileApi.resetSection` or `profileApi.resetAll`, clears all form drafts, edit states, and temporary variables, updates tab badge counts to 0, and reloads authoritative state via `loadProfileAndResumes(false)`.
  - Master Resume PDF & Isolation Safety: Confirmed that `master_resumes` and all job applications, tailored resumes, and user accounts remain completely untouched and preserved. User isolation is strictly enforced via `current_user.id`.
  - Comprehensive Testing & Verification: Added 3 new backend integration tests in `test_profile_and_resume.py` (`test_reset_individual_profile_sections`, `test_reset_all_profile_preserves_master_resume`, `test_reset_user_isolation`) -> 13 passed (100%). Added 4 comprehensive Playwright E2E tests in `profile_reset_save.spec.js` asserting database deletion and draft clearing across page reloads (`page.reload()`) with Master Resume PDF preservation -> 4 passed (100%). Workflow E2E tests pass 100%. All frontend assets built cleanly.

- **Epic 28 — Layout-Aware Master Resume Ingestion via PyMuPDF4LLM & Markdown Normalization**:
  - Architectural Upgrade: Upgraded primary master resume PDF text extraction in `PdfService.extract_text_from_pdf` to use `pymupdf4llm.to_markdown(file_path, write_images=False)`. Preserved the legacy raw stream text extraction as `extract_text_from_pdf_plain` for regression comparison.
  - Markdown Normalization Pipeline: Implemented `clean_resume_markdown` in `backend/app/services/pdf_service.py` ensuring parsed text integrates seamlessly into downstream section detection:
    - Normalizes `<br>` to `\n` to restore paragraph and bullet structure inside table-detected cells.
    - Strips HTML wrapper tags (`<u>`, `</u>`, etc.) without disturbing text content.
    - Cleans table row separators (`|---|`) and strips line-boundary pipes while preserving interior pipes (`|`) used in role titles and tech lists.
    - Strips markdown formatting (headers `#`, bold `**`, strikethrough `~~`, italics `*`/`_`, page-break rules).
    - Normalizes non-standard bullet symbols (`[•●▪◦*\ufffd]`) to standard `- ` markers and joins hyphenated line breaks.
  - Link Extraction Isolation: Maintained `extract_links_from_pdf` completely untouched, extracting native PyMuPDF PDF link annotations with coordinate bounding boxes.
  - Dependency Management: Added `pymupdf4llm>=1.24.10,<2.0.0` to `backend/requirements.txt`, verified 100% compatible with existing `PyMuPDF==1.28.2`.
  - Comprehensive Debug Tooling: Updated `debug_extraction.py` in workspace root to print RAW (plain), MARKDOWN (raw), and CLEANED text alongside character counts, line counts, and section-key comparisons across test fixtures and candidate resumes.

- **Epic 29 — Local LLM-First Master Resume Ingestion, Whole-Document Extraction & Categorized Skill Pipeline**:
  - Dual-Extraction Comparator: Structured `PdfService.extract_text_from_pdf` to execute both `_extract_markdown` and `_extract_plain`. Automatically selects Markdown output ONLY if `len(sections_md) >= len(sections_plain)` AND `lines_md >= 0.85 * lines_plain`, otherwise cleanly falls back to plain extraction. Preserves public `extract_text_from_pdf_plain` and raises explicit `ValueError` when both streams yield zero readable characters.
  - Whole-Resume LLM Parsing: Unified resume parsing into a single comprehensive local Ollama call in `OllamaProvider.extract_full_resume_structure` (temperature 0, num_ctx 8192, thinking disabled `think: False`, 300s timeout, single retry on invalid JSON). Structured outputs are validated against Pydantic models in `backend/app/services/ai/resume_llm_schemas.py` (`LLMPersonalInfo`, `LLMEducationItem`, `LLMExperienceItem`, `LLMProjectItem`, `LLMCertificationItem`).
  - Strict Anti-Fabrication Grounding: Implemented `_appears_in_source` normalized alphanumeric containment check across all extracted items (personal summary, degree, institution, company, role, project title, and each bullet text). Dropped any hallucinated items or bullets not grounded in the source text. Enforced regex overriding for exact contact info (email, phone, LinkedIn, GitHub) and per-section deterministic fallback when LLM returns zero valid items.
  - Chunked Skill Extraction & Categorization Pipeline: Designed `SkillPipeline` in `backend/app/services/skill_pipeline.py`. Splits resume text into 1500-char line-bounded chunks, extracts candidate technical and professional skills via LLM, grounds each skill via `appears_in_source`, deduplicates, detects inline label hints via regex (`LABEL_LINE_PATTERN`), and categorizes in batches of 30 into 22 canonical categories (16 technical + 6 professional/business categories, defaulting unrecognized categories to `Other`).
  - Project Re-upload Deduplication: Added `normalize_project_title` (lowercase, link badge stripping `[GitHub]`/`[Live]`, non-alphanumeric removal) and `is_same_project_title` using `difflib.SequenceMatcher >= 0.9` in `profile_service.py`. Incoming projects are deduplicated within the list and skip already-existing profile records on re-upload unless `overwrite_existing=True`. Added within-list deduplication to experience, education, and certifications.
  - Deterministic JD Experience Range Parser & Matching: Added `parse_jd_experience` in `ollama_provider.py` recognizing "0-2 years", "0 to 2 years", "0–2 yrs", "1-3 years", "2+ years", "at least 3 years", "minimum 5 years", and "fresher"/"entry level" (min 0). Overrides LLM extraction with deterministic `min_years`, `max_years`, and `experience_range`. Stores `min_years` in existing `experience_years` DB column and `max_years` in `raw_analysis` JSON (0 migrations). Displays full experience range in API and UI. In `matching_service.py`, treats `min_years` as the qualification threshold so candidate with 0 years qualifies for "0 to 2 years".
  - Data Integration & Non-Breaking Storage: Handled skill dicts (`{"name": ..., "category": ...}`) and legacy string skills uniformly in `ProfileService.compare_extracted_data_with_profile` and `apply_extracted_data_to_profile`. Leveraged existing `CandidateSkill.category` database column with 0 schema migrations or frontend contract breaks required.
  - Verification & Test Coverage: Added 5 comprehensive automated tests in `backend/tests/test_llm_first_parsing.py`, unit test for deterministic experience parser in `test_jd_analysis.py`, and project re-upload deduplication test in `test_profile_and_resume.py`. All 42 tests across 6 core test suites passing with 100% success.

## Completion standard
- Backend & frontend servers actively running and healthy (FastAPI on 8005, Vite on 5173).
- Frontend production bundle cleanly built with Vite (`npm run build`).
- PDF compilation verified working in under 1 second without timing out.
- JD extraction verified extracting comprehensive skillsets and accurate years.
- All constitutional rules and architecture constraints respected (local-first, zero telemetry, non-fabrication, version immutability, modular monolith).

## Current next step
Ready for end-user testing and production usage at `http://localhost:5173`.

## Locked top-level product areas
1. Auth
2. Profile
3. Workspace
4. Applications

## Locked architecture
Modular monolith with React + FastAPI + PostgreSQL, plus local Ollama, local file storage, and local LaTeX during V1 development.

## Locked design
Cream/off-white editorial/modern neo-brutalist SaaS visual direction inspired by the supplied reference image, adapted rather than copied. Workspace is a progressive workflow, not a giant vertically stacked page.

## Locked stack
React, Vite, JavaScript, Tailwind CSS, Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Alembic, Ollama, PyMuPDF, LaTeX, Pytest, Playwright, Postman, Git/GitHub, Docker/Docker Compose, GitHub Actions.

## Runtime placement
- React: Docker application environment; local Vite development is allowed for fast iteration
- FastAPI: Docker
- PostgreSQL: Docker with persistent volume
- Ollama: local/native
- LaTeX: included in the backend Docker image

## QA test management
- Manual and automation testing are maintained in separate module-wise Excel workbooks.
- Test cases are added and execution results are logged after the relevant feature reaches its testing stage.
- CI checks and merge must pass before the project advances to the next feature.

## Known TBD items
- Standardized local Ollama model: `qwen3:4b-instruct` (supports fast local structured extraction, hybrid resume parsing, and tailoring).
- Deployment target (intentionally TBD for V1 local-first product)

## Known non-goals
No autonomous job applications, no fabricated qualifications, no recruiter portal, no candidate ranking, no V1 job-board integrations, no unnecessary infrastructure additions.

## Current issues
None. Epics 0 through 29 verified and passing.
