# PrivateResume - Architecture Decision Records

## ADR-001 - Use a modular monolith
**Status:** Accepted

**Context:** PrivateResume has multiple domains but is V1-local-first and maintained as a focused product.

**Decision:** Build one FastAPI application with modular internal services.

**Reason:** Provides separation of concerns without distributed-system overhead.

**Alternatives considered:** Microservices.

**Why not:** No demonstrated V1 need for independent service deployment or scale.

## ADR-002 - Use PostgreSQL
**Status:** Accepted

**Context:** The domain contains relational entities, ownership, versions, and linked records.

**Decision:** Use PostgreSQL as the primary database.

**Reason:** Strong relational modeling, constraints, transactions, and familiar SQL behavior fit the domain.

**Alternative:** MongoDB.

**Why not:** The core domain is relational and benefits from explicit foreign keys and relational integrity.

## ADR-003 - Use Ollama for local AI
**Status:** Accepted

**Context:** Privacy-first/local-first AI is a central product principle.

**Decision:** Integrate Ollama through an AI service abstraction.

**Reason:** Keeps the default AI workflow local and isolates provider-specific code.

**Open point:** Exact model will be benchmarked later.

## ADR-004 - Use deterministic matching after structured extraction
**Status:** Accepted

**Context:** Pure LLM scoring can be opaque and unstable for a critical product metric.

**Decision:** Use deterministic matching logic after structured JD/candidate extraction, with AI used for language interpretation/explanations where helpful.

**Reason:** Improves consistency and explainability.

## ADR-005 - Use LaTeX for final resume generation
**Status:** Accepted

**Context:** The product must generate a controlled PDF using the candidate's template.

**Decision:** AI produces approved structured content; LaTeX controls formatting; compiler generates PDF.

**Reason:** Separates content intelligence from deterministic presentation and makes output repeatable.

## ADR-006 - Use application-level Docker with native Ollama
**Status:** Accepted - Revised

**Context:** PrivateResume is local-first, but the application should also be reproducible on another compatible machine. The product contains multiple runtime components: React, FastAPI, PostgreSQL, and LaTeX, while Ollama has host GPU/model-runtime considerations.

**Decision:** Use Docker Compose for React, FastAPI, and PostgreSQL. Include the LaTeX compiler in the backend image. Keep Ollama native on the host during V1.

**Reason:** This packages the main application runtime and database environment while avoiding unnecessary GPU/container complexity for local AI inference.

**Alternative considered:** Containerize Ollama as well.

**Why not:** Host GPU/driver integration and model storage can add unnecessary local complexity for the V1 product. The application communicates with Ollama through the backend service boundary, so Ollama can remain a local prerequisite.

## ADR-007 - Four top-level product areas
**Status:** Accepted

**Context:** The workflow has multiple states but should remain easy to navigate.

**Decision:** Auth, Profile, Workspace, Applications. Workspace stages are progressive states within one area.

**Reason:** Avoids navigation clutter and keeps the core task flow cohesive.

## ADR-008 - Evidence-based human approval
**Status:** Accepted

**Context:** Tailoring should improve representation without inventing qualifications.

**Decision:** Every material AI-generated change should be reviewable and grounded in candidate evidence; final generation requires candidate approval.

**Reason:** Supports factuality, user control, and explainability.


## ADR-009 - Feature-based development with short-lived Git branches
**Status:** Accepted

**Context:** PrivateResume is being built feature-by-feature and should teach a realistic collaborative development workflow.

**Decision:** Each meaningful feature is developed on a short-lived feature branch, tested at the appropriate layers, reviewed through a pull request, and merged into `main`. There is no permanent `develop` branch.

**Reason:** This provides practical experience with branch isolation, review, CI, regression testing, and integration without unnecessary branching complexity.

**Trade-off:** A solo developer performs the review workflow personally, but the project still preserves the same engineering discipline used in team development.


## ADR-010 - Maintain manual and automation test-case management
**Status:** Accepted

**Context:** PrivateResume should demonstrate both software engineering quality and practical QA skills.

**Decision:** Maintain two module-wise test-case workbooks: one for manual testing and one for automation. Populate them as features are completed, tested, reviewed, and merged.

**Reason:** Separating manual and automation evidence makes coverage, execution history, and QA contribution easier to demonstrate without mixing test design with implementation code.

## ADR-011 - Personal LaTeX Template Package Manager with Universal AST Injection
**Status:** Accepted

**Context:** Candidates have preferred LaTeX templates (e.g. FAANGpath, Trey Hunner, Modern CV) and should not be forced into a single rigid document structure.

**Decision:** Provide a Template Package Manager in Candidate Profile accepting `.tex` files or `.zip` archives. Use universal regex AST injection that identifies and populates candidate sections across `\begin{rSection}`, `\cvsection`, and standard `\section*` blocks. Support instant one-click fallback to the system default ATS template.

**Reason:** Empowers candidates with personalized resume aesthetics while maintaining 100% deterministic, automated content tailoring.

## ADR-012 - Hardened Offline Subprocess LaTeX Compilation
**Status:** Accepted

**Context:** Running `pdflatex` on user-uploaded templates can encounter missing packages, syntax errors, or prompt hangs if MiKTeX attempts to query remote CTAN servers over the network.

**Decision:** Execute `pdflatex` exclusively with `-interaction=nonstopmode -halt-on-error -disable-installer -no-shell-escape` inside an isolated temporary directory. Automatically inject native TeX link macros (`\providecommand{\href}`) and paragraph spacing shims into templates.

**Reason:** Guarantees sub-second compilation, prevents network-induced timeouts, and ensures safe execution with zero arbitrary command execution privileges.

## ADR-013 - Multi-Cycle Workspace Isolation with Automatic Application Pipeline Logging
**Status:** Accepted

**Context:** Completing an application cycle should not leave stale draft state or overwrite prior tailored versions when starting a new intake.

**Decision:** When a candidate downloads a tailored PDF in Stage 5, the system automatically registers the application in the Applications pipeline (status `applied`) and resets the workspace draft state to Stage 1. Filter active workspace queries by `status=active` to prevent applied jobs from persisting in active draft views.

**Reason:** Enforces a clean slate for subsequent job applications and eliminates cognitive clutter.

## ADR-014 - Layout-Aware Master Resume Ingestion with PyMuPDF4LLM and Markdown Normalization
**Status:** Accepted

**Context:** PyMuPDF raw stream text extraction (`page.get_text("text")`) lacks layout and block awareness in modern resumes containing multi-column layouts, horizontal section dividing lines, and boxed metadata. In real-world resumes, physical stream order often led to header interleaved text (e.g., location extracted as candidate name) and missed section breaks.

**Decision:** Integrate `pymupdf4llm.to_markdown` as the primary text extraction engine within `PdfService.extract_text_from_pdf` (preserving `extract_text_from_pdf_plain` for legacy comparison), paired with a deterministic `clean_resume_markdown` post-processing pipeline that:
1. Replaces `<br>` table cell line breaks with `\n` to restore multi-line paragraph boundaries.
2. Strips HTML wrapper tags (`<u>`, `</u>`, etc.) without disturbing text.
3. Removes table row borders (`|---|`) and strips line-boundary pipes while preserving interior pipes (`|`) used in role titles and tech lists.
4. Strips markdown syntax (headers `#`, bold `**`, strikethrough `~~`, italics `*`/`_`, horizontal rules) to match the plain text expectations of `segment_sections` and downstream section extractors.
5. Normalizes bullet glyphs (`[•●▪◦*\ufffd]`) into standard `- ` markers and joins hyphenated line breaks.

**Reason:** Preserves the existing `extract_text_from_pdf(file_path: str) -> str` signature and downstream regex parser contracts without requiring architectural changes, while significantly improving candidate name recognition, section segmentation, and bullet structure.

**Alternatives considered:** Raw PyMuPDF4LLM Markdown without cleaning (rejected: markdown headers `#` and table pipes `|` broke regex heading detection), Docling / OCR (rejected: excessive dependencies violating frozen stack boundaries and local-first privacy principles).

