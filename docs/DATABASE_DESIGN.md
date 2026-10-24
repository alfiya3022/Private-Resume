# PrivateResume - Database Design & Schema Specification

**RDBMS**: PostgreSQL 15 (Alpine)  
**Host / Port**: `localhost:5433` (Docker container: `private-resume-db`)  
**ORM / Migration**: SQLAlchemy 2.0 + Alembic

---

## 1. Database Philosophy & Invariants

1. **Relational Dominance**: Core entities (Users, Profiles, Experiences, Projects, Jobs, Applications) use strongly-typed relational schemas with foreign key constraints.
2. **Selective JSONB**: AI analysis outputs, tailored section payloads, and extracted skill bags utilize JSON/JSONB to accommodate schema evolution without frequent database migrations.
3. **Multi-Tenant User Isolation**: Every user-owned table contains a `user_id` foreign key with `ON DELETE CASCADE`. All query routines filter by `user_id == current_user.id`.
4. **Historical Immutability**: `TailoredResume` records and their compiled `ResumeArtifact` files are immutable snapshots. Editing a master profile does not mutate historical versions or submitted resumes.
5. **Application Linkage**: Every `Application` points to both the originating `job_id` and the exact `tailored_resume_id` submitted.

---

## 2. Entity Relationship Overview

```text
┌──────────────┐       1:1       ┌────────────────────┐
│    users     ├────────────────►│ candidate_profiles │
└───┬───┬───┬──┘                 └─────────┬──────────┘
    │   │   │                              │ 1:N
    │   │   │      ┌───────────────────────┴───────────────────────┐
    │   │   │      ▼               ▼               ▼               ▼
    │   │   │  ┌───────┐    ┌─────────────┐   ┌──────────┐   ┌───────────────┐
    │   │   │  │skills │    │ experiences │   │ projects │   │  educations   │
    │   │   │  └───────┘    └─────────────┘   └──────────┘   └───────────────┘
    │   │   │                                                      ▲
    │   │   │                                                      │ 1:N
    │   │   │                                              ┌───────┴───────┐
    │   │   │                                              │certifications │
    │   │   │                                              └───────────────┘
    │   │   │ 1:1
    │   │   └──────────────────────► ┌───────────────────┐
    │   │                            │   master_resumes  │
    │   │                            └───────────────────┘
    │   │ 1:N
    │   └──────────────────────────► ┌───────────────────┐       1:1       ┌──────────────────┐
    │                                │       jobs        ├────────────────►│ job_requirements │
    │                                └─────────┬─────────┘                 └──────────────────┘
    │                                          │ 1:N
    │                                          ▼
    │                                ┌───────────────────┐       1:1       ┌──────────────────┐
    │                                │  tailored_resumes ├────────────────►│  match_analyses  │
    │                                └─────────┬─────────┘                 └──────────────────┘
    │                                          │ 1:N
    │                                          ▼
    │                                ┌───────────────────┐
    │                                │  resume_artifacts │
    │                                └───────────────────┘
    │ 1:N
    └──────────────────────────────► ┌───────────────────┐
                                     │   applications    │
                                     └───────────────────┘
```

---

## 3. Schema Definitions

### 3.1 `users`
Primary identity and authentication table.
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_users_email ON users(email);
```

### 3.2 `candidate_profiles`
Anchor profile for a candidate.
```sql
CREATE TABLE candidate_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    headline VARCHAR(255),
    summary TEXT,
    phone VARCHAR(50),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_candidate_profiles_user_id ON candidate_profiles(user_id);
```

### 3.3 Profile Sub-Collections
- **`skills`**: `(id, profile_id, name, category, proficiency_level, created_at)`
- **`experiences`**: `(id, profile_id, company, title, location, start_date, end_date, is_current, bullets JSONB, created_at)`
- **`projects`**: `(id, profile_id, name, description, technologies JSONB, project_url, start_date, end_date, bullets JSONB, created_at)`
- **`educations`**: `(id, profile_id, institution, degree, field_of_study, grade, start_date, end_date, created_at)`
- **`certifications`**: `(id, profile_id, name, issuer, issue_date, credential_url, created_at)`

### 3.4 `jobs`
Target opportunity records.
```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    job_url VARCHAR(1000),
    salary VARCHAR(100),
    raw_jd_text TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_jobs_user_id ON jobs(user_id);
CREATE INDEX ix_jobs_status ON jobs(status);
```

### 3.5 `job_requirements`
Structured requirement extraction output for a target opportunity.
```sql
CREATE TABLE job_requirements (
    id SERIAL PRIMARY KEY,
    job_id INTEGER UNIQUE NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    required_skills JSONB DEFAULT '[]' NOT NULL,
    preferred_skills JSONB DEFAULT '[]' NOT NULL,
    languages JSONB DEFAULT '[]' NOT NULL,
    frameworks JSONB DEFAULT '[]' NOT NULL,
    databases JSONB DEFAULT '[]' NOT NULL,
    tools JSONB DEFAULT '[]' NOT NULL,
    cloud JSONB DEFAULT '[]' NOT NULL,
    responsibilities JSONB DEFAULT '[]' NOT NULL,
    qualifications JSONB DEFAULT '[]' NOT NULL,
    experience_years VARCHAR(100),
    soft_skills JSONB DEFAULT '[]' NOT NULL,
    raw_analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_job_requirements_job_id ON job_requirements(job_id);
```

### 3.6 `match_analyses`
Deterministic skill and evidence classification matrix.
```sql
CREATE TABLE match_analyses (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    match_score INTEGER NOT NULL,  -- 0 to 100 percentage
    matched_skills JSONB DEFAULT '[]' NOT NULL,
    weak_skills JSONB DEFAULT '[]' NOT NULL,
    missing_skills JSONB DEFAULT '[]' NOT NULL,
    unsupported_claims JSONB DEFAULT '[]' NOT NULL,
    evidence_matrix JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_match_analyses_job_id ON match_analyses(job_id);
```

### 3.7 `tailored_resumes`
Versioned tailored resume content snapshots.
```sql
CREATE TABLE tailored_resumes (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    version_number INTEGER DEFAULT 1 NOT NULL,
    parent_version_id INTEGER REFERENCES tailored_resumes(id),
    status VARCHAR(50) DEFAULT 'draft' NOT NULL,
    target_role VARCHAR(255),
    content JSONB NOT NULL,  -- summary, skills, experience, projects, education
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_tailored_resumes_job_id ON tailored_resumes(job_id);
CREATE INDEX ix_tailored_resumes_user_id ON tailored_resumes(user_id);
```

### 3.8 `resume_artifacts`
Compiled document storage pointers.
```sql
CREATE TABLE resume_artifacts (
    id SERIAL PRIMARY KEY,
    tailored_resume_id INTEGER NOT NULL REFERENCES tailored_resumes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL,  -- 'pdf' or 'tex'
    file_path VARCHAR(1000) NOT NULL,
    file_size INTEGER NOT NULL,
    compilation_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_resume_artifacts_tailored_resume_id ON resume_artifacts(tailored_resume_id);
```

### 3.9 `applications`
Application tracking pipeline records.
```sql
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    tailored_resume_id INTEGER NOT NULL REFERENCES tailored_resumes(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'applied' NOT NULL,
    applied_date DATE DEFAULT CURRENT_DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_applications_user_id ON applications(user_id);
CREATE INDEX ix_applications_status ON applications(status);
```

### 3.10 `master_resumes`
Ingested candidate master resume PDF records, raw text, and structured extraction data. A strict 1:1 relationship per user is enforced via Alembic migration `011_enforce_single_master_resume_per_user`.
```sql
CREATE TABLE master_resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash VARCHAR(64),
    raw_text TEXT NOT NULL,
    extracted_data JSONB,  -- structured profile entities (migration 010)
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_master_resumes_user_id UNIQUE (user_id)
);
CREATE INDEX ix_master_resumes_id ON master_resumes(id);
CREATE UNIQUE INDEX ix_master_resumes_user_id ON master_resumes(user_id);
```

---

## 4. Migration Governance
All migrations are authored using Alembic under [`backend/alembic/versions/`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/backend/alembic/versions). Schema alterations must be accompanied by an Alembic migration script; raw SQL alterations directly against production databases are prohibited.
