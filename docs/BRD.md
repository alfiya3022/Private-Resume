# PrivateResume - Business Requirements Document

## Purpose
Define the business problem, expected business value, stakeholders, scope, and measurable outcomes for PrivateResume.

## Business problem
Job seekers repeat manual resume-tailoring work across multiple tools: they maintain a master resume, analyze a job description, rewrite content, edit a template, validate the PDF, and track the application separately. Sensitive resume information may also be sent to third-party AI services.

## Business objective
Provide one local-first workflow that reduces repetitive tailoring effort while preserving factual accuracy, candidate control, privacy, and application history.

## Primary business user
Job seeker / candidate.

## Core business value
- Reduce repetitive resume-tailoring effort.
- Make job/resume alignment easier to understand.
- Keep AI-generated tailoring grounded in genuine candidate evidence.
- Keep AI processing local by default through Ollama.
- Provide a controlled final PDF generation workflow.
- Keep application history linked to the exact resume version used.

## Business rules
1. AI recommendations never authorize fabricated qualifications.
2. Missing skills are not instructions to invent skills.
3. Candidate approval is required before final resume generation.
4. Historical tailored resume versions remain immutable.
5. Applications reference the exact submitted resume version.
6. User-owned information is isolated by authorization.
7. Estimated Job Match is an internal estimate, not an employer ATS score.

## Scope
The V1 scope follows the PRD and includes authentication, candidate profile, master resume management, job/JD management, analysis, matching, tailoring, PDF generation, validation, and application tracking.

## Out of scope
Automatic applications, recruiter workflows, candidate ranking, job-board platform features, autonomous AI actions, unnecessary infrastructure, and multi-provider AI support.

## Success measures
- Critical workflow can be completed end-to-end.
- Important failure paths produce safe, understandable outcomes.
- Historical resume/application relationships remain correct.
- Core workflows have meaningful unit/integration/API/E2E/regression coverage.
- CI protects the merged `main` branch.
