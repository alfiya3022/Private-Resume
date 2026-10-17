# PrivateResume - Testing Standards and Quality Workflow

## Purpose
Testing is part of implementation, not a final phase.

Use:
- Pytest for unit and backend/database integration tests.
- Postman for API exploration, manual contract checks, negative scenarios, and repeatable collections.
- Playwright for critical browser E2E workflows and browser regression.
- GitHub Actions for automated checks on pushes and pull requests.

HTTPX is not a required project test tool at this stage.

## Non-negotiable principles
1. Test observable behavior and contracts.
2. Every meaningful feature needs relevant failure-oriented tests.
3. Assert meaningful outcomes and invariants.
4. Keep tests deterministic and isolated.
5. Do not mock away the behavior being tested.
6. Never use production data or secrets in tests.
7. Never claim tests were run unless they were actually run.
8. Do not add tests merely to inflate counts.

## Test levels
### Unit - Pytest
Use for focused logic: validation, matching, parsing helpers, versioning, claim/evidence checks, and state transitions.

### Integration - Pytest
Use real application components and an isolated test database for database behavior, transactions, ownership, migrations, persistence, and version relationships.

### API - Postman + automated backend tests
Use Postman for exploratory/manual verification and repeatable collections. Use automated backend tests for repeatable API behavior.

### E2E - Playwright
Use for high-value browser workflows and affected regression journeys.

### Regression
Run relevant existing tests whenever a change can affect them. Every practical bug fix should gain a regression test.

### Smoke
Run focused smoke checks after meaningful startup, configuration, deployment, or integration changes. Do not rerun them repeatedly for reassurance.

## Stage-specific minimum expectations
| Change | Minimum expectation |
|---|---|
| Business logic | Pytest normal, boundary, invalid cases |
| Model/migration | Integration tests for constraints and persistence |
| Service/transaction | Unit + relevant integration tests |
| API endpoint | Automated backend tests + Postman checks |
| Auth/authorization | Unauthenticated, ownership, forged-ID, cross-user cases |
| Upload/parsing | Type, size, corrupt/unreadable, path-safety, cleanup |
| AI integration | Provider failure, timeout, malformed output, unsupported claims |
| Resume generation | Success, compilation failure, missing assets, PDF invariants |
| Frontend workflow | Playwright critical path and important negative path |
| Bug fix | Regression test that reproduces the defect, where practical |
| Startup/config | Relevant smoke and regression checks |

## Verification-command policy
Do not run or request commands merely for reassurance. Use focused commands when required by acceptance criteria, setup, diagnosis, or an explicit technical decision.

## Code inspection policy
When additional repository context is necessary and it is not already available, request the specific file or relevant section rather than repeatedly retrieving large amounts of code.

## Feature gate
A feature is complete only when acceptance criteria, relevant tests, edge cases, security checks, documentation, and CI/merge requirements are satisfied.
