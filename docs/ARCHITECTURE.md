# Architecture

## High-level components

```
+--------------------------+        +--------------------------+
|  Next.js 15 (Frontend)   | <----> |  Django REST (Backend)   |
|  App Router · TS         |  HTTPS |  JWT auth · RBAC         |
|  Tailwind · Recharts     |  JSON  |  Modular apps · Service  |
+--------------------------+        +-----+--------+-----------+
                                          |        |
                                  +-------v--+   +-v-------+
                                  | Postgres |   |  Redis  |
                                  +----------+   +----+----+
                                                      |
                                              +-------v-------+
                                              | Celery worker |
                                              | + beat        |
                                              +-------+-------+
                                                      |
                                              +-------v-------+
                                              | AI/OCR engine |
                                              +---------------+
```

## Backend layout (clean architecture)

Every domain app follows the same module layout:

```
apps/<domain>/
  models.py          # ORM entities
  enums.py           # (in apps/core/enums.py - shared)
  serializers.py     # (de)serialization + per-field validation
  filters.py         # django-filter FilterSets for list endpoints
  services.py        # Business rules (state transitions, scoring, etc.)
  views.py           # DRF viewsets, only orchestrate
  urls.py            # router registrations
  admin.py           # Django admin
  tests.py           # Pytest unit tests
```

The dependency direction is: `views → services → models`. Serializers are
also allowed to call services for cross-entity validation. This keeps
business rules out of the HTTP layer and makes them re-usable from
management commands, Celery tasks, and the admin.

`apps/core` contains cross-cutting concerns and is depended on by all other
apps:

- `models.py` — `BaseModel` (UUID PK + timestamps + soft delete)
- `enums.py` — All `TextChoices` shared across apps
- `permissions.py` — Role-based DRF permission classes
- `responses.py` — `envelope()` helper for the standard response shape
- `exceptions.py` — DRF exception handler that wraps errors in the envelope
- `pagination.py` — Standard pagination class
- `middleware.py` — `AuditLogMiddleware` writing to `notifications.AuditLog`

## Database design

Conceptual ER (key tables only):

```
Company 1───* Department
   │           │
   │           *
   │       1───┘
   *
   └───* User ────* Audit ────* Task ────* EvidenceFile
                       │           │           │
                       │           │           1
                       │           │           │
                       │           │           AIExtractionResult
                       │           *
                       │           Review
                       │
                       *───* Department  (audits.departments m2m)
                       │
                       *───── Finding ──── CorrectiveAction
```

Highlights:
- All tables inherit `BaseModel` so every row has UUID PK, `created_at`,
  `updated_at`, and `deleted_at` (soft delete).
- Indexes are added on hot filter columns (`status`, FK pairs).
- `Task.submission_data` and `TaskTemplate.schema` use JSONB on Postgres,
  enabling the dynamic template engine without per-template tables.
- `Audit.compliance_score` is denormalised at close time by the service
  layer so dashboard queries don't recompute on every request.

## API design

- Versioned at `/api/v1/`.
- Every response uses the same envelope:
  ```json
  { "success": true, "data": ..., "message": "OK", "errors": null }
  ```
- Lists are paginated; the pagination object lives inside `data`.
- All errors (validation, permission, 404, 500) flow through
  `apps.core.exceptions.api_exception_handler` to produce the same shape.
- OpenAPI schema is exposed at `/api/schema/` via drf-spectacular, with
  Swagger UI at `/api/docs/` and ReDoc at `/api/redoc/`.

## Authentication & RBAC

JWT (SimpleJWT) with refresh-token rotation and blacklist on logout.
Tokens are stored in `localStorage` on the frontend and attached as
`Authorization: Bearer ...`. A 401 in any response triggers a single
refresh attempt before redirecting to `/login`.

Three roles are enforced via DRF permission classes:

| Role | Permission class |
|------|------------------|
| Admin | `IsAdmin` |
| Auditor | `IsAuditor` |
| Department user | `IsDepartmentUser` |
| Admin OR Auditor | `IsAdminOrAuditor` |

Querysets are also tenant-/role-filtered in `get_queryset()` so users only
see their own org's data even if a permission check is misconfigured.

## AI engine

The verification flow (`apps/ai_engine/services.py:verify_evidence`) is
deliberately conservative:

1. Extract text from the evidence file (`extractors.py` dispatches on
   extension to pdfplumber / python-docx / openpyxl / pytesseract).
2. Run lightweight rule checks (presence, dates, completeness).
3. Compute a confidence score and choose one of:
   `pass`, `fail`, `requires_human`, `inconclusive`.
4. Persist `AIExtractionResult` and surface it to the auditor.

The auditor **always** has the final say. The system never auto-approves
based on AI output. Phase 10 is structured so the rules engine can grow
without changing the surrounding plumbing.

## Frontend layout

```
src/
  app/
    layout.tsx            # root html/body
    page.tsx              # redirect based on auth
    login/page.tsx        # public
    (app)/                # route group requiring auth
      layout.tsx          # sidebar + header + auth guard
      dashboard/...       # role-routed dashboards
      audits/             # list + detail
      tasks/              # list + detail
  components/
    ui/                   # shadcn-style primitives (button, card, ...)
    layout/               # sidebar + header
    dashboard/            # stat-card, charts
  lib/
    api.ts                # axios instance + envelope unwrapping + 401 refresh
    utils.ts              # cn(), formatters, status colours
  store/
    auth-store.ts         # Zustand auth store
  hooks/
    use-auth.ts           # useRequireAuth() with role gating
  types/
    index.ts              # mirrors backend serializer shapes
```

State management is intentionally minimal: Zustand for auth, React local
state for everything else. Forms use react-hook-form + Zod resolvers.

## Security

- JWT rotation + blacklist on logout
- HTTPS / HSTS / secure cookies in `production.py`
- Rate limits via DRF throttles
- CSRF middleware enabled (irrelevant to API but kept for admin)
- File upload validation: extension allow-list + size limit + SHA-256
- All writes audited via `AuditLogMiddleware` into `AuditLog` table
- Tenant filtering enforced in querysets, not just permissions
- ORM only — no raw SQL — protects against SQL injection
- DRF JSONRenderer escapes unsafe HTML — protects against XSS

## Deployment

`docker-compose.yml` (dev): Postgres + Redis + Django runserver + Celery
worker + Celery beat + Next.js dev server.

Production should use the same images but with:
- `DJANGO_SETTINGS_MODULE=compliance_audit.settings.production`
- Gunicorn instead of `runserver`
- Nginx in front (config provided in `docker/nginx/nginx.conf`)
- `npm run build && npm start` for the frontend (Next standalone output)
- A managed Postgres + Redis (don't run on a single host)
- Real secrets pulled from a secrets manager rather than `.env`

## Testing

```bash
# backend
cd backend && pytest

# frontend  (placeholder — Jest config not wired in this MVP)
cd frontend && npm test
```

## Phase coverage

| Phase | Status in this MVP |
|-------|-------------------|
| 1. Architecture | ✅ Complete |
| 2. Backend foundation | ✅ Complete |
| 3. Database design | ✅ Complete (auto-generated migrations) |
| 4. Authentication | ✅ Complete |
| 5. Admin module | ✅ Complete (UI: dashboard; API: full CRUD) |
| 6. Audit management | ✅ Complete (lifecycle + transitions) |
| 7. Template engine | ⚠ Skeleton (model + JSON schema, no UI renderer) |
| 8. Task management | ✅ Complete (full state machine) |
| 9. Evidence upload | ✅ Validated upload + storage abstraction |
| 10. AI verification | ⚠ Working pipeline, conservative rules |
| 11. Auditor review | ⚠ Models + APIs (Review/Finding/CorrectiveAction); no dedicated UI page |
| 12. Dashboards | ✅ Complete (admin / auditor / department) |
| 13. Reports | ✅ PDF + CSV via ReportLab |
| 14. Physical audit | ✅ Same workflow as other tasks (`task_type=physical`) |
| 15. Notifications | ⚠ Models + Celery beat schedule, no UI page |
| 16. Security hardening | ✅ Per-environment settings + middleware |
| 17. DevOps | ✅ Docker compose + Nginx config |

`⚠` items are explicitly built as skeletons with the same architectural
patterns as the complete modules — extending them follows the same
`models → serializers → services → views → urls` layout.
