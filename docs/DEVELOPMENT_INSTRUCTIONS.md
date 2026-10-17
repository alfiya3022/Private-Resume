# PrivateResume — Development & AI Coding Instructions

## Purpose

These instructions define how PrivateResume must be developed, tested, verified, documented, and maintained.

They supplement the existing project documentation, including the Project Constitution, AGENTS.md, PROJECT_STATE.md, development plan, test plan, security documentation, and architecture decision records.

When these instructions conflict with an existing locked project decision, do not silently override the decision. Stop, explain the conflict, and request approval to reopen it.

---

## 1. Core Development Principles

PrivateResume must be developed as a real software product, not as a collection of generated code or screens.

Use this development loop:

Requirement -> Design -> Implement -> Test -> Review -> Document -> Commit/PR -> Next task

Work on one meaningful feature or task at a time.

Do not implement future features just because they may eventually be useful.

Do not change the architecture, technology stack, API contract, database design, or UI direction without a clear reason and explicit approval.

Prefer simple, readable engineering over unnecessary sophistication.

---

## 2. Human-Readable Code

Code must look like it was written by a competent developer who understands the project, not like automatically generated enterprise boilerplate.

Prefer:
- straightforward Python and JavaScript
- clear variable and function names
- small focused functions
- simple control flow
- readable React components
- explicit logic
- standard framework patterns
- the minimum abstraction needed for the current requirement

Avoid:
- unnecessary factories
- unnecessary abstract base classes
- unnecessary interfaces
- speculative configuration systems
- excessive dependency injection
- clever one-liners
- advanced syntax when simple syntax is clearer
- premature optimization
- unnecessary wrapper functions
- excessive generic components
- duplicate utilities
- unused flexibility

A more advanced pattern is justified only when the current requirement genuinely benefits from it.

---

## 3. Minimal-Code Rule

Only write code that is genuinely required for the current task.

Do not add:
- unused imports
- unused variables
- unused parameters
- placeholder implementations presented as finished functionality
- speculative features
- unnecessary configuration
- duplicate validation
- redundant error handling
- unnecessary abstractions
- unnecessary dependencies

Comments should explain non-obvious reasoning, not restate what the code already says.

Do not create a stub simply to make an architecture look complete.

If functionality is intentionally deferred, state that clearly.

---

## 4. Security Must Be Built Into Development

Security is part of implementation, not a final checklist.

For relevant features, consider:
- input validation
- SQL injection protection
- authorization and user-data ownership checks
- secure password hashing
- secure secret handling
- file type and content validation
- upload size limits
- safe filenames and storage paths
- path traversal prevention
- safe LaTeX template ZIP handling
- XSS risks
- safe error responses
- appropriate CORS configuration
- authentication abuse/rate-limiting considerations
- safe handling of user-supplied URLs where the backend performs network requests
- dependency hygiene
- protection of PII and resume contents

Never hardcode secrets.

Never expose stack traces, SQL details, internal filesystem paths, credentials, tokens, private prompts, or sensitive resume/JD content to users or logs.

Security controls should be proportional to the actual application. Do not add complex security infrastructure merely to make the project look enterprise-grade.

---

## 5. Testing Strategy

Testing must happen continuously throughout development.

Do NOT wait until the entire project is finished.

Use multiple testing levels because each level answers a different question.

### 5.1 Unit Tests

Use unit tests for focused business logic that can be tested in isolation.

Examples:
- matching rules
- scoring calculations
- validation helpers
- versioning rules
- parsing helpers
- claim/evidence checks

Add unit tests as the relevant feature is implemented.

Reason:

Unit tests are fast and locate logic failures precisely.

### 5.2 Integration Tests

Use integration tests when multiple application components must work together.

Examples:
- FastAPI + service + PostgreSQL
- creating a job and persisting it
- saving an analysis
- creating a tailored resume version
- linking an application to an exact resume version
- authorization against database-owned resources

Reason:

Unit tests cannot prove that database queries, transactions, services, and API behavior work together correctly.

### 5.3 API Tests

Use HTTPX/Pytest to verify important API contracts.

Test:
- valid requests
- invalid requests
- authentication failures
- authorization failures
- missing resources
- duplicate/conflicting operations
- correct response structure
- correct status codes
- important error responses

Reason:

The API is the contract between the React frontend and FastAPI backend.

### 5.4 End-to-End Tests

Use Playwright for the most important browser workflows.

Critical PrivateResume journey:

Register
-> Upload Master Resume
-> Review Profile
-> Create Job
-> Analyze JD
-> View Match
-> Generate Tailored Resume
-> Edit / Ask AI
-> Generate PDF
-> Validate
-> Save Application

Reason:

E2E tests verify that the major parts of the product actually work together from the user's point of view.

Do not attempt to E2E-test every tiny UI interaction.

### 5.5 Regression Testing

Regression testing is required whenever an existing feature could be affected by a change.

Examples:
- changing authentication -> rerun authentication and protected-resource tests
- changing database models -> rerun affected integration/API tests
- changing resume versioning -> rerun version immutability and application-link tests
- changing workspace state transitions -> rerun affected Playwright flow
- changing AI output validation -> rerun tailoring and unsupported-claim tests

Maintain the critical E2E journey as a regression suite.

Reason:

A new feature must not silently break behavior that already worked.

### 5.6 Smoke Testing

Use lightweight smoke checks when there is a meaningful build/startup change or after a significant integration milestone.

Examples:
- application starts
- backend health endpoint responds
- database connection works
- frontend loads
- basic API request succeeds

Reason:

Smoke tests answer: "Is the application fundamentally alive?"

Do not repeatedly run smoke commands simply for reassurance when no relevant change has occurred.

### 5.7 Negative and Edge-Case Testing

For each feature, identify the important ways it can fail.

Examples already relevant to PrivateResume:
- empty JD
- invalid PDF
- oversized upload
- unreadable PDF
- missing master resume
- Ollama unavailable
- malformed AI output
- LaTeX compilation failure
- missing template files
- invalid ZIP
- unauthorized resource ID
- repeated/concurrent save attempts
- unsupported claim introduced during AI editing

Reason:

Happy-path tests alone do not demonstrate reliability.

### 5.8 Security Testing

At the stage where security-sensitive functionality is introduced or changed, test relevant controls.

Examples:
- unauthorized resource access
- user-data isolation
- invalid upload handling
- path traversal attempts
- unsafe input handling
- secret leakage
- error-message leakage

Reason:

Security failures often occur at boundaries and should be tested close to when those boundaries are implemented.

---

## 6. Testing by Development Stage

Use the following practical progression.

### During a small logic change
Primary focus:
- unit tests
- relevant edge cases

### During API/service/database integration
Primary focus:
- unit tests
- integration tests
- API tests
- authorization tests

### During a user-facing workflow
Primary focus:
- component/UI behavior as appropriate
- API tests
- Playwright E2E for important workflows

### After a feature is integrated
Primary focus:
- affected regression tests
- broader smoke check when relevant

### Before a milestone or release
Primary focus:
- full relevant automated test suite
- critical E2E regression journey
- security checks
- build/integration verification

Do not force every kind of test onto every tiny change. Use the smallest appropriate test set for the risk and scope of the change.

---

## 7. Verification-Command Policy

Do NOT ask the user to run commands merely to reassure yourself that something "probably works."

Verification commands should be provided when:
- we are diagnosing an actual bug
- a setup step genuinely requires verification
- a test/command is itself part of the feature's acceptance criteria
- the result is necessary to make a technical decision

Do not create unnecessary command-run loops.

Avoid:
- "Run this just to confirm."
- "Run this again so I can make sure."
- "Run another command even though the previous result already established it."

If a previous result already proves the required condition, use that result.

Reason:

Development time should be spent building and testing the product, not repeatedly proving unchanged conditions.

---

## 8. Code Inspection / File-Reading Policy

When code or repository content needs to be inspected, do not repeatedly retrieve the same files or large portions of the repository just for reassurance.

First determine exactly what code is needed.

If the required code is not already available in the current context:
1. Ask the user to provide/upload the specific file or relevant section.
2. State why that file is needed.
3. Inspect only what is necessary.
4. Do not repeatedly fetch the same content unless the file has changed or additional context is genuinely required.

Do not use repeated content-retrieval commands to compensate for uncertainty.

Reason:

This saves context, reduces unnecessary conversation/tool usage, and keeps debugging focused.

---

## 9. When Editing an Existing File

Always identify the exact location of a change.

Use instructions such as:
- "Add this immediately below the import block."
- "Add this after the existing `create_app()` function."
- "Replace the current `X` function with the following."
- "Add this route immediately after `GET /profile`."

When useful, show:
1. What to locate.
2. What to add/replace.
3. The resulting relevant section.

Never assume the user knows where a new code block belongs.

Reason:

Precise editing instructions prevent accidental duplication and incorrect placement.

---

## 10. Feature Completion / Definition of Done

A feature is NOT complete simply because its code exists.

Before marking a feature done, confirm that the relevant conditions are satisfied:
- requirement implemented
- correct architecture used
- appropriate validation included
- authorization/security considered
- important edge cases handled
- relevant tests written
- relevant tests pass
- UI/API integration completed where applicable
- errors handled appropriately
- no unnecessary code introduced
- documentation/state updated when required
- code is committed with a meaningful Git message

This follows the project's existing Definition of Done.

---

## 11. AI Coding-Agent Behavior

AI is an implementation assistant, not the authority on project direction.

Before changing architecture, API contracts, database design, technology choices, or UI structure:
1. Read the relevant project documentation.
2. Check the current project state.
3. Check locked decisions.
4. Explain the proposed change.
5. Explain why it is needed.
6. Explain alternatives and trade-offs when relevant.
7. Ask for approval if it reopens a locked decision.

Do not invent decisions.

Do not silently add technologies.

Do not silently expand scope.

Do not rewrite unrelated files.

Do not "improve" code that is outside the current task unless a concrete issue requires it.

---

## 12. Documentation and Project State

After a meaningful milestone:
- update `PROJECT_STATE.md` with verified work only
- update `CHANGELOG.md` when appropriate
- update decision documentation only when a decision intentionally changes
- record new architectural decisions as ADRs when appropriate

Never record work as completed if it was not actually implemented and verified.

Reason:

The repository documentation is the long-term project memory and helps keep AI coding sessions aligned.

---

## 13. Dependency Policy

Before adding a dependency:
1. Identify the concrete requirement.
2. Determine whether the standard library or existing stack is sufficient.
3. Explain why a new dependency provides meaningful value.
4. Consider maintenance, security, and complexity costs.
5. Add it only when justified.

Do not add libraries because they are popular, trendy, or merely convenient for a small task.

After compatibility is verified, freeze the working dependency set.

---

## 14. Scope Control

Never introduce features because they "might be useful later."

Examples of currently excluded infrastructure/features include:
- Redis
- Celery
- Kafka
- Kubernetes
- Terraform
- MongoDB
- GraphQL
- Elasticsearch
- vector databases
- LangChain
- LangGraph
- microservices
- autonomous job applications

These remain excluded unless a real requirement or verified technical constraint justifies reopening the decision.

---

## 15. Communication Style During Development

For every meaningful step, explain:

### What
What are we implementing?

### Why
Why is it needed?

### Design
How does it fit the approved architecture?

### Files
Which files will be created or changed?

### Testing
Which tests will verify it?

### Edge Cases
What important failures must be handled?

### Security
What security considerations apply?

### Next Step
What comes after this?

Then ask for the user's agreement before moving to the next step.

Do not jump ahead without approval.

---

## 16. Golden Rule

Build the smallest correct solution that:
- satisfies the requirement
- follows the locked architecture
- is secure enough for the actual risk
- is tested at the appropriate level
- is readable by the developer
- is explainable in an interview
- does not create unnecessary complexity

Professional does not mean complicated.

Simple, tested, well-reasoned code is the goal.
