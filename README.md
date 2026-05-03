# AI-Assisted Smart Compliance Reporting and Audit Management System

An enterprise-grade compliance audit management platform that replaces Excel-based tracking, email audits, and manual document collection with a unified AI-assisted workflow.

> **AI Limitation Principle**: AI assists auditors with low-risk repetitive checks (OCR, field extraction, expiry validation, completeness). High-risk audits, legal decisions, physical inspections, and final approvals always remain with human auditors.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Tech Stack](#tech-stack)
3. [User Roles](#user-roles)
4. [Quick Start (Docker)](#quick-start-docker)
5. [Local Development (without Docker)](#local-development-without-docker)
6. [Project Structure](#project-structure)
7. [Seed Users](#seed-users)
8. [API Documentation](#api-documentation)
9. [Testing](#testing)
10. [Deployment](#deployment)

---

## Architecture

The platform is a **monorepo** with two top-level applications and a Docker-orchestrated infrastructure layer:

```
+--------------------------+        +--------------------------+
|  Next.js 15 (Frontend)   | <----> |  Django REST (Backend)   |
|  - App Router            |  HTTPS |  - JWT auth, RBAC        |
|  - TypeScript / Tailwind |  JSON  |  - Modular apps          |
|  - Zustand / Recharts    |        |  - Service layer         |
+--------------------------+        +-----+--------+-----------+
                                          |        |
                                  +-------v--+   +-v-------+
                                  | Postgres |   |  Redis  |
                                  | (JSONB)  |   | (broker)|
                                  +----------+   +----+----+
                                                      |
                                              +-------v-------+
                                              | Celery worker |
                                              | + beat        |
                                              +---------------+
                                                      |
                                              +-------v-------+
                                              | AI/OCR engine |
                                              | (Tesseract,   |
                                              |  pdfplumber)  |
                                              +---------------+
```

The backend follows **clean architecture** with `models / serializers / services / views` separation. Cross-cutting concerns (audit logging, RBAC, exception handling, response envelope) live in `apps/core`.

## Tech Stack

**Frontend:** Next.js 15 (App Router), TypeScript, TailwindCSS, shadcn-style UI, Zustand, React Hook Form, Zod, Axios, Recharts, Framer Motion

**Backend:** Django 5, Django REST Framework, PostgreSQL 16, JWT (SimpleJWT), Celery 5, Redis 7

**AI / OCR:** Tesseract, pdfplumber, PyMuPDF, python-docx, pandas, openpyxl, spaCy

**Infrastructure:** Docker, Docker Compose, Nginx, Gunicorn, WhiteNoise

## User Roles

| Role | Capabilities |
|------|--------------|
| **Admin** | Manages company, departments, users, roles, templates; sees global dashboards and reports |
| **Auditor** | Schedules audits, creates tasks, reviews evidence, triggers AI verification, approves/rejects, raises findings, assigns corrective actions, generates reports |
| **Department User** | Views assigned tasks, uploads evidence, fills checklists, resolves corrective actions, views department dashboard |

## Quick Start (Docker)

```bash
# 1. Clone and enter
cd Ty_Final_project

# 2. Copy environment templates
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Build and start the stack
docker compose up --build

# 4. In another terminal, seed the database
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_data

# 5. Open the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1/
# API docs (Swagger): http://localhost:8000/api/docs/
# Django admin: http://localhost:8000/admin/
```

## Local Development (without Docker)

You'll need: Python 3.11+, Node 20+, PostgreSQL 14+, Redis 6+.

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then edit DB credentials
python manage.py migrate
python manage.py seed_data
python manage.py runserver

# Celery (separate terminal)
celery -A compliance_audit worker -l info
celery -A compliance_audit beat -l info

# Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Project Structure

```
Ty_Final_project/
├── backend/                      # Django + DRF API
│   ├── compliance_audit/         # Project settings, celery, urls
│   │   └── settings/             # base / development / production
│   ├── apps/                     # Feature-based modules
│   │   ├── core/                 # Base models, mixins, RBAC, middleware
│   │   ├── authentication/       # JWT login/refresh/logout
│   │   ├── companies/            # Company entity
│   │   ├── departments/          # Departments
│   │   ├── users/                # Custom user with role
│   │   ├── audits/               # Audit lifecycle (FULL)
│   │   ├── tasks/                # Compliance tasks (FULL)
│   │   ├── templates_engine/     # Dynamic template engine (skeleton)
│   │   ├── evidence/             # File upload + S3 abstraction
│   │   ├── ai_engine/            # OCR + extraction pipeline
│   │   ├── reviews/              # Auditor review workflow
│   │   ├── reports/              # PDF / CSV report generation
│   │   ├── notifications/        # Email + in-app reminders
│   │   └── analytics/            # Dashboard aggregations
│   ├── manage.py
│   └── requirements.txt
├── frontend/                     # Next.js 15 app
│   └── src/
│       ├── app/                  # App router pages
│       ├── components/           # UI + feature components
│       ├── lib/                  # API client, auth, utils
│       ├── store/                # Zustand stores
│       ├── hooks/                # React hooks
│       └── types/                # Shared TypeScript types
├── docker/                       # Dockerfiles + nginx config
├── docker-compose.yml            # Dev orchestration
└── README.md
```

## Seed Users

After running `python manage.py seed_data`, you can log in with:

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@acme.test` | `Admin@12345` |
| Auditor | `auditor@acme.test` | `Auditor@12345` |
| Department | `dept@acme.test` | `Dept@12345` |

The seed script also creates: 1 company (Acme Corp), 3 departments (Finance, IT, HR), 1 active audit, 1 task template, and 5 sample tasks.

## API Documentation

After starting the backend, OpenAPI/Swagger docs are auto-generated at:

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema JSON: http://localhost:8000/api/schema/

All endpoints are versioned under `/api/v1/`.

## Testing

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Deployment

Production deployment uses `docker-compose.prod.yml` with:
- Gunicorn behind Nginx for the backend
- Multi-stage built Next.js standalone server
- Postgres with persistent volume
- Redis for Celery broker
- Configurable env via `.env.production`

See `docs/DEPLOYMENT.md` for the full guide (TLS, secrets, scaling).

---

## Implementation Status

This MVP scaffold delivers:

**Fully implemented end-to-end:** authentication (JWT), RBAC, companies, departments, users, audits, tasks, dashboard analytics (admin/auditor/department), seed data, Docker orchestration.

**Skeleton with models + endpoints:** templates_engine, evidence storage, ai_engine, reviews, reports, notifications. These have working models, serializers, and basic CRUD; the heavier processing (real OCR, PDF generation, email sending) has clear extension points marked `TODO(phase-X)`.

The architecture is consistent across all modules so that filling in skeletons follows the same patterns established in the fully-implemented apps.
