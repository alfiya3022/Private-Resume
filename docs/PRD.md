# PrivateResume - Product Requirements Document

## Status
Locked baseline as of 2026-09-23.

## Product vision
PrivateResume is a local-first, privacy-first AI-powered platform that helps job seekers analyze job descriptions, compare them against genuine candidate evidence, generate evidence-based tailored resumes, produce ATS-oriented PDF resumes through a controlled LaTeX template, validate the result, and track job applications.

## Problem
The current workflow is fragmented: candidates maintain a master resume, copy job descriptions into AI tools, tailor content manually, edit in a document/template tool, validate separately, and track applications elsewhere. Sensitive resume data may also be sent to third-party AI services.

## Core product principle
AI recommends -> Candidate reviews -> Candidate edits/approves -> System generates final resume.

PrivateResume may optimize the representation of genuine qualifications but must not fabricate skills, experience, projects, certifications, achievements, qualifications, or metrics.

## Primary user
Job seeker / candidate. Recruiter and employer workflows are out of scope for V1.

## V1 scope
- Master resume PDF upload and parsing
- Candidate profile creation/review
- Job description input and structured analysis
- Resume-to-job comparison
- Estimated job match metric
- Evidence inspection
- Tailored resume generation
- Human editing and section-level AI assistance
- Resume versioning
- LaTeX template package upload
- LaTeX compilation to PDF
- Resume validation
- Application tracking
- Local Ollama integration
- Authentication and user data isolation
- Automated tests, Docker development support, and CI

## Non-goals
- Automatic job applications
- LinkedIn/Indeed auto-apply
- Recruiter portal
- Candidate ranking
- Fake qualification generation
- Guaranteed ATS score or interview outcome
- Full job-board platform
- Social network
- Interview platform
- Dozens of resume templates
- Google Sheets integration in V1
- Multi-LLM provider support in V1
- Autonomous AI applications

## Inputs
1. Master Resume: PDF only in V1. The source PDF is preserved.
2. Job Description: pasted text, with optional company, title, location, URL, and salary/CTC.

## Core workflow
Master Resume + Job Description -> Analysis -> Match -> Tailoring -> Human Review -> LaTeX -> PDF -> Validation -> Application Record.

## Functional requirements
- FR-01 Upload and validate master resume PDF.
- FR-02 Parse PDF into structured candidate information.
- FR-03 Let candidate review and correct extracted data.
- FR-04 Preserve historical tailored resumes when the master profile changes.
- FR-05 Create a job record with original JD preserved.
- FR-06 Analyze JD into structured requirements.
- FR-07 Preserve original JD text.
- FR-08 Compare profile/evidence against JD requirements.
- FR-09 Produce human-readable match analysis.
- FR-10 Provide an estimated match metric with clear labeling.
- FR-11 Generate evidence-based tailored resume content.
- FR-12 Prevent unsupported claims.
- FR-13 Allow resume editing.
- FR-14 Support section-level AI editing.
- FR-15 Generate LaTeX from approved structured content.
- FR-16 Compile PDF and provide preview/download.
- FR-17 Validate final resume output.
- FR-18 Save tailored resume versions.
- FR-19 Save application records.
- FR-20 Support application statuses.
- FR-21 View previous applications and linked artifacts.
- FR-22 Use local Ollama.
- FR-23 Handle meaningful failures gracefully.
- FR-24 Persist candidate, job, analysis, tailored resume, artifact, and application data.

## Non-functional requirements
Security, privacy, reliability, performance, maintainability, testability, observability, portability, CI/CD, code quality, UX clarity, explainability, AI factuality, human approval, historical version immutability, and future deployment flexibility.

## Match metric policy
The product must use a label such as "Estimated Job Match". It must not be presented as an employer ATS score. ATS compatibility is a separate set of concrete checks such as text extractability, standard headings, contact information, page count, and placeholder detection.

## Acceptance philosophy
Requirements are complete only when they are objectively testable and the relevant error/edge cases are addressed.
