# PrivateResume - Database Design

## Database choice
PostgreSQL.

### Why
The core domain is relational: users own profiles, jobs, resumes, analyses, tailored versions, artifacts, and applications. PostgreSQL provides constraints, foreign keys, transactions, and indexing suitable for this model.

## Core entities
- User
- Candidate Profile
- Skill
- Candidate Skill
- Project
- Project Skill / Evidence association
- Experience
- Education
- Certification
- Master Resume
- Job
- Job Requirement
- Match Analysis
- Match Result
- Tailored Resume
- Resume Artifact
- Application

## Key relationships
```text
User -> Candidate Profile
Candidate Profile -> Skills / Projects / Experience / Education / Certifications
User -> Master Resumes / Jobs / Applications
Job -> Job Requirements
Candidate + Job -> Match Analysis -> Tailored Resume -> Resume Artifacts
Application -> Job + exact Tailored Resume version
```

## Important invariants
1. A user can own multiple jobs.
2. A user can have multiple tailored resume versions.
3. A job can have multiple tailored resume versions.
4. An application points to the exact tailored resume version submitted.
5. Historical tailored resume snapshots are immutable.
6. Master profile changes do not rewrite historical application/resume snapshots.
7. All user-owned rows are protected by authorization checks.

## Structured data vs JSONB
Use relational tables for core entities and relationships. Use selective JSONB for evolving AI outputs or analysis payloads where rigid columns would add unnecessary churn.

### Why
This keeps the domain queryable and constraint-friendly while allowing AI outputs to evolve. Whole database records should not be dumped into JSON just for convenience.

## Indexing
Index foreign keys and common lookup fields used by authenticated user views, job/application lists, and version retrieval. Add additional indexes only after evidence of query need.

## Transactions
Operations that create linked records or versions should use transactions so partial state is not persisted.

## Migrations
Alembic manages schema changes. Manual database drift is not part of the development workflow.
