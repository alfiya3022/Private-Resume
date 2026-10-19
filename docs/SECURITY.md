# PrivateResume - Security & Privacy Specification

**Objective**: Protect candidate Personally Identifiable Information (PII), uploaded resumes, tailored career snapshots, AI analysis payloads, and application histories from unauthorized disclosure, data leakage, or malicious execution.

---

## 1. Security Architecture & Threat Model

```text
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                         │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / HTTP + Security Headers
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              SecurityHeadersMiddleware                      │
│  - X-Content-Type-Options: nosniff                          │
│  - X-Frame-Options: SAMEORIGIN                              │
│  - X-XSS-Protection: 1; mode=block                          │
│  - Strict CORS Origin Validation                            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Authentication & Authorization Layer             │
│  - OAuth2 Bearer JWT Token Validation                       │
│  - get_current_active_user Dependency Injection             │
│  - Row-Level Tenant Isolation Enforcement                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  PostgreSQL  │       │ Isolated     │       │ Local Ollama │
│  (Parametric │       │ Temp Build   │       │ Subsystem    │
│   SQLAlchemy │       │ Directory    │       │ (Local Port  │
│   Queries)   │       │ (pdflatex)   │       │  11434 Only) │
└──────────────┘       └──────────────┘       └──────────────┘
```

---

## 2. Authentication & Identity Controls
1. **Password Hashing**: Passwords are hashed using standard `bcrypt` with salt rounds via `passlib`. Plaintext passwords are never written to disk or logged.
2. **Stateless JWT Tokens**: Authentication uses HMAC-SHA256 (`HS256`) signed JSON Web Tokens with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
3. **Protected Endpoint Gates**: All private endpoints enforce authentication through FastAPI's `Depends(get_current_active_user)`.

---

## 3. Row-Level Multi-Tenant Data Isolation
- **Tenant Integrity**: Every profile, master resume, job opportunity, requirement analysis, match result, tailored resume, compiled artifact, and application record contains a non-nullable `user_id` foreign key.
- **Invariable Authorization Filter**:
  ```python
  # Standard pattern across all queries:
  entity = db.query(Model).filter(Model.id == entity_id, Model.user_id == current_user.id).first()
  if not entity:
      raise HTTPException(status_code=404, detail="Entity not found or access unauthorized")
  ```
- **Zero Cross-Tenant Leakage**: Attempting to query or manipulate another user's ID yields a strict `404 Not Found` to prevent entity enumeration.

---

## 4. File Upload & Ingestion Hardening
1. **MIME & Extension Validation**: Master resume uploads accept `.pdf` only; LaTeX template package manager accepts `.tex` files or `.zip` packages exclusively.
2. **Safe Filename Generation**: Uploaded files are renamed using secure UUID prefixes (e.g. `e4cabc7b_Alfiya_resume.pdf`) rather than trusting user-supplied paths, preventing path traversal attacks (`../`).
3. **Storage Segregation**: User files are stored in `backend/storage/` outside of executable code and frontend public web directories.
4. **ZIP Archive Sanitization**: Template `.zip` packages are inspected upon extraction to prevent zip-slip directory traversal vulnerabilities.

---

## 5. LaTeX Subprocess Sandboxing & Sanitization
Subprocess execution of `pdflatex` carries potential risks if unconstrained. PrivateResume hardens compilation through multiple layers:

### 5.1 Subprocess Execution Parameters
```python
cmd = [
    "pdflatex",
    "-interaction=nonstopmode",  # Never prompt interactively
    "-halt-on-error",            # Abort immediately on syntax error
    "-disable-installer",        # Prevent MiKTeX from hanging on CTAN network calls
    "-no-shell-escape",          # Strictly forbid external shell binary execution
    f"{output_base_name}.tex",
]
```
- `-no-shell-escape`: Completely disables the `\write18{...}` TeX primitive, making it impossible to invoke host shell commands through uploaded templates.
- `-disable-installer`: Forbids automatic network package downloading from untrusted remote mirrors.
- Isolated Temporary Directory: Compilation executes inside `tempfile.TemporaryDirectory()`. Generated temporary files (`.aux`, `.log`, `.fls`) are immediately purged after PDF output extraction.

### 5.2 Input Sanitization & Escaping
All dynamic candidate strings (names, companies, bullets, summaries) pass through [`latex_escape()`](file:///c:/Users/alfiy/Documents/Downloads/Private%20Resume/backend/app/services/latex_service.py#L25-L45) before interpolation:
- Reserved characters (`&`, `%`, `$`, `#`, `_`, `{`, `}`) are escaped with backslashes (`\&`, `\%`, etc.).
- Special characters (`~`, `^`, `\`) are transformed into safe typesetting primitives (`\textasciitilde{}`, `\textasciicircum{}`, `\textbackslash{}`).

---

## 6. Data Privacy & Zero External Telemetry
- **Local AI Execution**: Ollama inference runs entirely on the host machine (`http://localhost:11434`). No prompts, candidate resumes, or job descriptions are transmitted to third-party APIs (OpenAI, Anthropic, or cloud aggregators).
- **Zero Third-Party Trackers**: No Google Analytics, telemetry beacons, Sentry cloud reporting, or external font trackers.
- **Sensitive Log Suppression**: Logging configuration suppresses request bodies, JWT tokens, and resume bullets from standard server stdout.

---

## 7. Security Headers & Network Hygiene
FastAPI injects defensive HTTP response headers on every request:
- `X-Content-Type-Options: nosniff` — Prevents MIME-sniffing exploits.
- `X-Frame-Options: SAMEORIGIN` — Mitigates clickjacking and framing attacks.
- `X-XSS-Protection: 1; mode=block` — Enables browser cross-site scripting filters.
- **Strict CORS Policy**: Restricted to authorized development origins (`localhost:5173`, `127.0.0.1:5173`). Wildcard `*` origins are strictly forbidden.
