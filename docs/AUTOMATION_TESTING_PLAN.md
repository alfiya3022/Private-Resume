# PrivateResume - Automation Testing Plan

## Purpose
Define the automated testing strategy for backend, API, browser, and CI verification.

## Tools
### Pytest
Use for unit tests and backend/database integration tests.

### Playwright
Use for critical browser workflows and browser regression.

### Postman
Use for manual API exploration plus repeatable collections for contract, negative, and smoke scenarios. Postman is not a replacement for automated unit/integration or E2E coverage.

### GitHub Actions
Use for automated checks on pushes and pull requests.

## Automation layers

### Unit
Fast isolated tests for business rules, parsing helpers, validation, matching, and versioning.

### Integration
Real application components with an isolated test database for persistence, constraints, transactions, and ownership behavior.

### API
Automated backend API behavior plus Postman collections for contract and negative checks.

### E2E
High-value Playwright workflows only. Do not automate every minor UI detail.

### Regression
Existing relevant automated tests run whenever a change can affect previous behavior. Every practical bug fix receives a regression test.

## Test design principles
- Assert meaningful behavior.
- Include invalid and boundary cases.
- Keep tests deterministic and independent.
- Avoid arbitrary sleeps.
- Do not mock away the behavior under test.
- Keep external boundaries mocked in unit tests and real in appropriate integration tests.
- Do not weaken assertions just to obtain a passing build.

## Automation gate
Before merge, relevant automated tests must pass and CI must pass. Test evidence is logged in the automation workbook.
