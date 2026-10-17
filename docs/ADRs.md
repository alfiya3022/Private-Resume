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
