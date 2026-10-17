# PrivateResume - Manual Testing Plan

## Purpose
Define the manual QA process used throughout PrivateResume.

## Manual test objectives
- Verify business requirements from a user's perspective.
- Validate UI behavior and workflows.
- Explore negative and boundary cases.
- Verify API behavior manually with Postman.
- Perform regression checks on affected existing functionality.
- Capture defects and execution evidence.

## Manual testing types
- Requirements-based functional testing
- UI testing
- Exploratory testing
- Boundary and negative testing
- API testing with Postman
- Smoke testing when warranted
- Regression testing
- Basic usability and accessibility checks
- Security-oriented manual checks at relevant boundaries

## Test case design
Every meaningful feature should have test cases with:
- identifier
- module/feature
- scenario
- preconditions
- test data
- steps
- expected result
- severity
- priority
- test type
- execution result
- evidence
- defect linkage

## Execution rule
Manual cases are executed after the corresponding implementation is testable. Results are logged in the module tab of the manual-testing workbook.

## Defect handling
For a failed case:
1. Record the actual result.
2. Record the defect ID when one is created.
3. Re-test after the fix.
4. Add or update a regression case when the defect represents a realistic future regression.

## Completion gate
A feature can advance only after required manual cases are executed, relevant defects are resolved or explicitly accepted, automation coverage is updated where applicable, CI passes, and the feature is merged.
