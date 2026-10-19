# PrivateResume - REST API Specification

**Version**: 1.0.0  
**Base URL**: `http://localhost:8005/api/v1`  
**Protocol**: HTTP/1.1 (JSON & Multipart/form-data)

---

## 1. Architectural Principles
- **Resource-Oriented URLs**: Nouns represent entities; HTTP verbs define standard actions (`GET`, `POST`, `PUT`, `DELETE`).
- **Stateless Bearer Authentication**: Protected endpoints require `Authorization: Bearer <JWT_TOKEN>`.
- **Multi-Tenant User Isolation**: All read/write operations enforce ownership against the authenticated user extracted from the JWT token.
- **Controlled Error Shape**: Predictable HTTP status codes accompanied by structured error payloads (`detail`).
- **AI Decoupling**: React never communicates with Ollama directly; all AI workflows are mediated through backend service layers.

---

## 2. Standard Status Codes & Error Responses

| Code | Status | Description |
| :--- | :--- | :--- |
| `200` | OK | Successful retrieval or update |
| `201` | Created | Resource successfully created |
| `400` | Bad Request | Malformed payload or validation error |
| `401` | Unauthorized | Missing, expired, or invalid JWT bearer token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Target entity does not exist or belongs to another user |
| `409` | Conflict | Resource conflict (e.g. duplicate email registration) |
| `422` | Unprocessable Entity | Pydantic validation failure |
| `500` | Internal Server Error | Server execution or compilation failure |

**Standard Error Schema**:
```json
{
  "detail": "Descriptive human-readable error explanation."
}
```

---

## 3. Endpoints

### 3.1 Health & Diagnostics
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | No | System liveness probe returning status of database, Ollama, and LaTeX. |
| `GET` | `/` | No | Basic root endpoint returning service version and operational mode. |

**Sample `/health` Response (`200 OK`)**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "development",
  "subsystems": {
    "database": "connected",
    "ollama": "connected",
    "latex": "available"
  }
}
```

---

### 3.2 Authentication (`/auth`)
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | No | Register a new user account with email, full name, and password. |
| `POST` | `/auth/login` | No | Authenticate via OAuth2 form data; returns JWT access token. |
| `GET` | `/auth/me` | Bearer | Retrieve profile information for the authenticated user. |

**Sample Login Request**:
- Content-Type: `application/x-www-form-urlencoded`
- Fields: `username=user@example.com`, `password=SecurePassword123`

**Sample Login Response (`200 OK`)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

---

### 3.3 Candidate Profile (`/profile`)
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/profile` | Bearer | Retrieve the candidate master profile with all sub-collections. |
| `PUT` | `/profile` | Bearer | Update candidate contact info, headline, and bio summary. |
| `POST` | `/profile/skills` | Bearer | Add a technical or soft skill category and skill item. |
| `DELETE` | `/profile/skills/{id}` | Bearer | Remove a skill entry. |
| `POST` | `/profile/experience` | Bearer | Add a work experience entry (company, title, dates, bullets). |
| `PUT` | `/profile/experience/{id}` | Bearer | Update an existing work experience record. |
| `DELETE` | `/profile/experience/{id}` | Bearer | Delete a work experience record. |
| `POST` | `/profile/projects` | Bearer | Add a project record (name, tech stack, url, bullets). |
| `PUT` | `/profile/projects/{id}` | Bearer | Update an existing project record. |
| `DELETE` | `/profile/projects/{id}` | Bearer | Delete a project record. |
| `POST` | `/profile/education` | Bearer | Add education credentials (degree, institution, dates, grade). |
| `PUT` | `/profile/education/{id}` | Bearer | Update education credentials. |
| `DELETE` | `/profile/education/{id}` | Bearer | Delete education credentials. |
| `POST` | `/profile/certifications` | Bearer | Add certification record (name, issuer, date, url). |
| `PUT` | `/profile/certifications/{id}` | Bearer | Update certification record. |
| `DELETE` | `/profile/certifications/{id}` | Bearer | Delete certification record. |
| `POST` | `/profile/template` | Bearer | Upload custom LaTeX template (`.tex` or `.zip` package). |
| `GET` | `/profile/template` | Bearer | Get metadata about active custom template or default status. |
| `DELETE` | `/profile/template` | Bearer | Delete custom template and revert to default ATS template. |

---

### 3.4 Master Resumes (`/resumes`)
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/resumes/upload` | Bearer | Ingest a master resume PDF; parses sections and populates profile. |
| `GET` | `/resumes` | Bearer | List all uploaded master resume files for candidate. |
| `GET` | `/resumes/{id}` | Bearer | Download or view the raw PDF master resume file. |
| `DELETE` | `/resumes/{id}` | Bearer | Delete an uploaded master resume file. |

---

### 3.5 Job Opportunities & Analysis (`/jobs`)
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/jobs` | Bearer | Create a new target opportunity with title, company, salary, and JD. |
| `GET` | `/jobs` | Bearer | List target opportunities (supports query parameter `?status=active`). |
| `GET` | `/jobs/{id}` | Bearer | Retrieve job details by ID. |
| `PUT` | `/jobs/{id}` | Bearer | Update job metadata, compensation, or raw JD text. |
| `DELETE` | `/jobs/{id}` | Bearer | Delete a job opportunity record. |
| `POST` | `/jobs/{id}/analyze` | Bearer | Trigger hybrid Ollama/deterministic JD requirement parsing. |
| `GET` | `/jobs/{id}/analysis` | Bearer | Retrieve existing structured JD requirements. |
| `POST` | `/jobs/{id}/match` | Bearer | Execute deterministic match evaluation against candidate profile. |
| `GET` | `/jobs/{id}/match` | Bearer | Retrieve existing match analysis and evidence matrix. |

**Sample Job Requirements Response (`200 OK`)**:
```json
{
  "id": 1,
  "job_id": 3,
  "required_skills": ["SQL", "SQL Server", "Stored Procedures", "Data Manipulation (DML)"],
  "preferred_skills": ["Coding / Scripting Languages", "Customer-Facing Experience"],
  "experience_years": "1 To 2 Years",
  "responsibilities": ["Administration including SQL backups", "Creating complex stored procedures"],
  "qualifications": ["B.E./B.Tech or equivalent degree", "Minimum 1 to 2 years experience in SQL"],
  "created_at": "2026-10-18T18:00:00Z"
}
```

---

### 3.6 Tailored Resumes & PDF Generation (`/tailored-resumes`)
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/jobs/{job_id}/tailor` | Bearer | Generate initial tailored resume draft grounded in profile facts. |
| `GET` | `/tailored-resumes/{id}` | Bearer | Fetch tailored resume content and current version number. |
| `PUT` | `/tailored-resumes/{id}` | Bearer | Save inline candidate edits across any section or heading. |
| `POST` | `/tailored-resumes/{id}/refine-section` | Bearer | "Ask AI to Polish" interactive refinement strictly bounded by facts. |
| `POST` | `/tailored-resumes/{id}/generate-pdf` | Bearer | Compile tailored content via pdflatex; saves and returns PDF artifact. |
| `GET` | `/tailored-resumes/{id}/artifacts` | Bearer | Retrieve compiled `.pdf` and `.tex` document paths and logs. |

---

### 3.7 Applications Pipeline (`/applications`)
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/applications` | Bearer | Log an application linked to a job and tailored resume version. |
| `GET` | `/applications` | Bearer | List tracked applications (optional filter: `?status=applied`). |
| `GET` | `/applications/{id}` | Bearer | Retrieve an individual application record. |
| `PUT` | `/applications/{id}` | Bearer | Update application status, interview notes, or applied date. |
| `DELETE` | `/applications/{id}` | Bearer | Remove an application from the tracking board. |

**Supported Application Statuses**:
- `saved`
- `applied`
- `assessment`
- `interview`
- `rejected`
- `offer`
- `withdrawn`
