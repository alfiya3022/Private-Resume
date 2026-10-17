# PrivateResume - Security and Privacy

## Security objective
Protect candidate PII, resumes, generated documents, AI analysis, and application history from unauthorized access or accidental disclosure.

## Authentication
- Passwords must be securely hashed; plaintext passwords are never stored.
- Protected endpoints require authenticated identity.
- Token/session handling must be secure and configurable.

## Authorization
Every user-owned resource must be checked against the authenticated user. Never trust resource IDs alone.

## User isolation invariant
User A must not be able to read, edit, delete, or download User B's profile, resume, job, analysis, tailored resume, artifact, or application.

## File upload security
- Validate MIME/type and actual file format.
- Enforce configured size limits.
- Store uploads outside executable code directories.
- Generate safe storage names rather than trusting user filenames.
- Prevent path traversal.
- Validate LaTeX ZIP contents before extraction.

## Resume and PII privacy
- Avoid logging resume text, JD text, contact details, and generated resume contents unless explicitly required and sanitized.
- Keep AI processing local by default through Ollama.
- Preserve transparency about where data is processed and stored.

## AI safety and factuality
- AI output is not authoritative.
- Unsupported claims must not be fabricated.
- Structured AI output must be validated before persistence.
- Human approval is required before final generation.

## Secrets and configuration
- Secrets live in environment configuration, not source control.
- `.env` is ignored by Git.
- `.env.example` contains variable names and safe examples only.

## Database security
- Use parameterized ORM/database operations.
- Enforce foreign keys and constraints.
- Use transactions for multi-record operations.

## Logging and observability
Logs should include useful operational context such as request IDs and error categories without exposing sensitive resume contents or credentials.

## Error handling
Return user-safe errors. Do not expose stack traces, SQL details, filesystem paths, tokens, or internal prompts to clients.

## Local-first does not mean automatically safe
Running locally reduces third-party exposure for the default AI path, but OS access, local backups, malware, file permissions, and browser security still matter.

## Security review checklist
Authentication, authorization, file validation, secret handling, PII logging review, path traversal checks, prompt/input validation, artifact access control, and error leakage review.
