# PrivateResume - Test Case Management

## Purpose
Define how manual and automated test cases are designed, organized, executed, and recorded.

## Two test-case workbooks
1. `PrivateResume_Manual_Test_Cases.xlsx`
2. `PrivateResume_Automation_Test_Cases.xlsx`

Each workbook is divided module-wise so that coverage and execution history can be reviewed independently for each product area.

## Module structure
The same module taxonomy is used in both workbooks:
- Auth
- Profile: Personal, Education, Experience, Projects, Skills, Certifications, Activities, Achievements
- Resume Template
- Master Resume
- Workspace / Job Input
- JD Analysis
- Match Analysis
- Evidence
- Tailored Resume
- AI Editing
- Versioning
- PDF Generation
- Validation
- Applications
- Settings

## Case lifecycle
Draft -> Ready -> Executed -> Passed / Failed / Blocked -> Retest -> Closed

The Excel templates intentionally contain column headers only at the start of the project. Actual test cases and execution results are added as the relevant features are completed.

## Manual workbook purpose
Records human-executed functional, UI, exploratory, API/Postman, negative, regression, usability, and security-oriented checks.

## Automation workbook purpose
Records automated test intent, automation level/tool, script location, expected assertions, CI execution, failures, and regression status.

## Severity vs priority
- Severity describes the impact of a defect.
- Priority describes how urgently the defect should be addressed.

## Feature release gate
A feature is eligible to move to the next feature only after:
1. implementation is complete;
2. relevant manual and automated tests are executed;
3. defects are handled or formally accepted;
4. relevant regression tests pass;
5. CI passes;
6. PR review is complete;
7. the branch is merged into `main`;
8. project state/documentation is updated.

## Integrity rules
- Never fabricate test results.
- Never mark a test as passed without evidence.
- Do not delete historical test execution results merely because a case later changes.
- Add a new version/row or appropriate history field for materially changed cases.
