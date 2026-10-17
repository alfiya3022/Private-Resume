# PrivateResume - Development Plan

## Implementation order
1. Epic 0 - Project Foundation
2. Epic 1 - Authentication & User Isolation
3. Epic 2 - Profile + Master Resume
4. Epic 3 - Job Management
5. Epic 4 - JD Analysis
6. Epic 5 - Resume-to-Job Matching
7. Epic 6 - Tailored Resume + Human Editing
8. Epic 7 - LaTeX + PDF Generation
9. Epic 8 - Resume Validation
10. Epic 9 - Application Tracking
11. Epic 10 - Testing, CI & Security Hardening
12. Epic 11 - UX Polish + Final Project Packaging

## Development loop
Requirement -> Acceptance Criteria/Test Design -> Feature Branch -> Implement -> Focused Tests -> Integration/Regression -> Review -> Document -> Commit -> Push -> CI -> PR/Merge -> Next feature

## Epic 0 - Project Foundation
- Initialize Git repository
- Create React/Vite frontend
- Create FastAPI backend
- Configure environment settings
- Configure SQLAlchemy and Alembic
- Configure Docker Compose and PostgreSQL persistent volume
- Create health checks
- Create basic error handling and logging
- Create design-system component foundation
- Create initial frontend routing and API client

## Epic 1 - Authentication
- Registration
- Login/logout
- Password hashing
- Token/session flow
- Protected routes
- Current-user dependency
- User isolation tests

## Epic 2 - Profile and master resume
- Profile CRUD
- PDF upload validation
- File storage
- PyMuPDF extraction
- Section detection
- Review/edit/save extracted data

## Epic 3 - Jobs
- Job CRUD
- JD persistence
- Workspace initial state

## Epic 4 - JD analysis
- Ollama provider abstraction
- Structured output validation
- Required/preferred requirement extraction
- Analysis persistence
- Job analysis UI

## Epic 5 - Matching
- Evidence model
- Deterministic matching rules
- Estimated job match metric
- Evidence detail UI

## Epic 6 - Tailoring
- Structured resume generation
- Section-level editing
- Ask AI flow
- Accept/reject
- Version creation

## Epic 7 - PDF generation
- LaTeX ZIP template validation
- Template storage
- Content injection
- Compilation
- Artifact persistence

## Epic 8 - Validation
- PDF generation checks
- Text extractability
- Headings and sections
- Placeholder detection
- Unsupported claim detection
- Validation UI

## Epic 9 - Applications
- Application CRUD
- Status workflow
- Resume-version linkage
- Notes/timeline
- Tracker UI

## Epic 10 - Quality
- Unit tests
- Integration tests
- Playwright critical flow
- CI checks
- Security hardening
- Logging review

## Epic 11 - Packaging
- Responsive polish
- Accessibility
- Loading/error/empty states
- README
- Architecture documentation
- Screenshots
- Demo data
- Final GitHub cleanup

## Definition of Done
A feature is done when the relevant requirement is implemented, validated, tested, integrated into the UI/API, error paths are handled, and the work is committed with a meaningful message.
