# PrivateResume - REST API Specification

## Base path
`/api/v1/`

## API principles
- Resource-oriented URLs
- HTTP verbs reflect the operation
- JSON for standard request/response bodies
- Multipart for PDF/ZIP uploads
- Authentication required for protected resources
- Consistent error format
- OpenAPI documentation through FastAPI

## Status code conventions
200 OK, 201 Created, 202 Accepted when asynchronous processing is introduced, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Validation Error, 500 Internal Server Error, 503 Service Unavailable.

## Authentication
- POST `/auth/register`
- POST `/auth/login`
- POST `/auth/refresh`
- GET `/auth/me`

Reason: authentication is a cross-cutting boundary and must exist before sensitive candidate data is exposed.

## Profile
- GET `/profile`
- PUT `/profile`
- GET/POST/PUT/DELETE `/profile/projects` and item routes
- Equivalent routes for experience, education, certifications, activities, achievements, skills

Reason: profile is the structured candidate source of truth.

## Master resumes
- POST `/resumes` - multipart PDF upload
- GET `/resumes`
- GET `/resumes/{resume_id}`
- DELETE `/resumes/{resume_id}`

Reason: master resumes are user-owned source documents and need a dedicated lifecycle.

## Jobs
- POST `/jobs`
- GET `/jobs`
- GET `/jobs/{job_id}`
- PUT `/jobs/{job_id}`
- DELETE `/jobs/{job_id}`
- POST `/jobs/{job_id}/analyze`
- POST `/jobs/{job_id}/match`

Reason: job records are the anchor for JD analysis, matching, tailoring, and application history.

## Tailored resumes
- POST `/jobs/{job_id}/tailor`
- GET `/tailored-resumes/{id}`
- POST `/tailored-resumes/{id}/edit`
- PUT `/tailored-resumes/{id}`
- POST `/tailored-resumes/{id}/generate-pdf`
- POST `/tailored-resumes/{id}/validate`
- GET `/tailored-resumes/{id}/artifacts`

Reason: tailored resumes are versioned user-owned artifacts associated with a specific job.

## Applications
- POST `/applications`
- GET `/applications`
- GET `/applications/{id}`
- PUT `/applications/{id}`
- DELETE `/applications/{id}`

Statuses: Saved, Applied, Assessment, Interview, Rejected, Offer, Withdrawn.

## AI boundary
React never calls Ollama directly. All AI processing flows through backend service endpoints.

## Error handling contract
The API should return a stable machine-readable error shape with a human-readable message. Internal stack traces and sensitive resume content must not be exposed to clients.

## Versioning
The `/v1` prefix allows controlled API evolution later without forcing immediate breaking changes.
