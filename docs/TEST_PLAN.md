# PrivateResume - Test Plan

## Testing objective
Verify that PrivateResume is correct, secure, explainable, and reliable across the critical user workflow.

## Test levels
### Unit
Test focused business logic in isolation.
Examples: matching rules, validation helpers, versioning rules.

### Integration
Test interactions between API, services, and PostgreSQL.
Examples: creating a job and persisting analysis; saving an application with an exact tailored resume version.

### End-to-end
Use Playwright for the critical browser journey.

## Critical E2E journey
```text
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
```

## Backend coverage areas
- authentication
- authorization / user isolation
- profile CRUD
- resume upload and file validation
- PDF parsing
- job CRUD
- JD analysis error handling
- matching and scoring rules
- tailoring and unsupported-claim protection
- version immutability
- LaTeX compilation failure handling
- validation service
- application lifecycle

## Frontend coverage areas
- auth states
- navigation and protected routes
- profile editing
- workspace state transitions
- evidence drawer
- resume editor
- PDF preview/validation state
- application tracker
- loading, empty, success, and error states

## Negative and edge tests
- empty JD
- invalid PDF
- oversized upload
- unreadable PDF
- missing master resume
- Ollama unavailable
- malformed AI output
- LaTeX compiler failure
- missing template files
- invalid ZIP
- unauthorized resource ID
- concurrent or repeated save attempts
- unsupported claim introduced during AI edit

## Test principles
1. Test behavior, not implementation details where possible.
2. Keep tests deterministic.
3. Cover important error paths.
4. Keep user-isolation tests explicit.
5. Treat the core workflow as a regression suite.


## Manual QA workflow
Manual testing covers requirements-based verification, exploratory testing, UI behavior, negative scenarios, API exploration with Postman, usability/accessibility checks where relevant, and release/regression verification.

## Automation workflow
Automation covers:
- Pytest for unit tests and backend/database integration tests.
- Playwright for critical browser workflows and browser regression.
- Postman collections for repeatable API contract and negative-scenario checks.
- GitHub Actions for repeatable automated checks on pushes and pull requests.

## Feature gate
A feature is not allowed to move to the next feature until its required implementation, test execution, defect handling, documentation update, CI checks, and PR merge are complete.

## Test-case management
Each feature is logged in module-specific tabs in the manual and automation Excel workbooks. Both workbooks are execution records, not substitutes for the automated test code itself.
