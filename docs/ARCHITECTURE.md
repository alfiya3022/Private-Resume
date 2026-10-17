# PrivateResume - Architecture

## Architectural style
PrivateResume uses a modular monolith. The backend is one deployable application with internally separated modules.

### Why
The product has several related domains but does not need microservice-level distribution. A modular monolith provides separation of concerns, simpler local development, easier transactions, and lower operational complexity.

### Why not microservices
Microservices would introduce service-to-service networking, deployment coordination, distributed failure handling, and more infrastructure without a demonstrated V1 requirement.

## High-level architecture
```text
React frontend
      | HTTP/REST
      v
FastAPI backend
      |
      +--> PostgreSQL
      +--> Ollama (local)
      +--> Local file storage
      +--> LaTeX compiler
```

The frontend never directly connects to PostgreSQL or Ollama.

## Layered backend
```text
HTTP route / router
        |
        v
Application/business service
        |
        +--> database
        +--> AI service
        +--> file storage
        +--> LaTeX / validation
```

## Backend module responsibilities
- auth: authentication and current-user access
- profile: structured candidate data
- resumes: master resume upload and management
- jobs: job and JD lifecycle
- analysis: JD analysis and match analysis orchestration
- tailoring: tailored resume generation and editing
- applications: application tracking
- ai service: provider abstraction and Ollama integration
- resume service: parsing and source resume workflows
- matching service: primarily deterministic classification and scoring
- latex service: template processing and PDF compilation
- validation service: final document checks
- storage service: local file persistence abstraction

## AI boundary
The application talks to an AI service abstraction rather than directly to Ollama from every feature.

Conceptual interface:
```text
AIService
  analyze_jd()
  analyze_resume()
  generate_match_analysis()
  tailor_resume()
  edit_resume_section()
        |
        v
OllamaProvider
```

### Why
Provider isolation allows model/provider changes later without spreading Ollama-specific code across the application.

## Deterministic vs AI responsibilities
Deterministic systems handle deterministic tasks such as persistence, validation rules, versioning, access control, file rules, and defined matching logic. AI handles language understanding and generation where appropriate.

## Matching model
Matching is primarily deterministic after structured extraction. AI may support language interpretation and explanation but should not be the only authority for a match result.

## Document pipeline
```text
Master PDF -> PyMuPDF -> raw text -> section detection -> structured candidate data

Approved resume content -> LaTeX template -> compiler -> PDF artifact -> validation
```

## Versioning invariant
Historical tailored resumes are immutable snapshots. Changes to the master profile must not rewrite historical submitted resumes.

## User isolation invariant
Every user-owned resource must be authorized against the authenticated user.

## Storage
Local filesystem is the V1 file storage mechanism. Cloud object storage is a future option, not a V1 requirement.

## Deployment posture
The product is local-first and cloud-capable later. Local AI processing is the default design intent.
