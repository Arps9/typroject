"""Seed the database with a working demo dataset.

Usage:
    python manage.py seed_data           # idempotent
    python manage.py seed_data --fresh   # wipe and reseed
"""
from __future__ import annotations

from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.audits.models import Audit
from apps.companies.models import Company
from apps.core.enums import (
    AuditStatus,
    AuditType,
    Priority,
    RiskLevel,
    TaskStatus,
    TaskType,
    UserRole,
)
from apps.departments.models import Department
from apps.tasks.models import Task
from apps.templates_engine.models import TaskTemplate
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed the database with a working demo dataset."

    def add_arguments(self, parser):
        parser.add_argument("--fresh", action="store_true",
                            help="Delete existing demo data first")

    def handle(self, *args, **options):
        if options["fresh"]:
            self.stdout.write(self.style.WARNING("Wiping demo data..."))
            Task.all_objects.all().delete()
            Audit.all_objects.all().delete()
            TaskTemplate.all_objects.all().delete()
            User.all_objects.exclude(is_superuser=True).delete()
            Department.all_objects.all().delete()
            Company.all_objects.all().delete()

        with transaction.atomic():
            company = self._create_company()
            depts = self._create_departments(company)
            admin = self._create_user(
                "admin@acme.test", "Admin@12345", UserRole.ADMIN,
                "Alice", "Admin", company, None,
            )
            auditor = self._create_user(
                "auditor@acme.test", "Auditor@12345", UserRole.AUDITOR,
                "Aaron", "Auditor", company, None,
            )
            dept_user = self._create_user(
                "dept@acme.test", "Dept@12345", UserRole.DEPARTMENT,
                "Diana", "Department", company, depts["Finance"],
            )

            template = self._create_template(company)
            audit = self._create_audit(company, depts, auditor)
            self._create_tasks(audit, depts, dept_user, template)

        self.stdout.write(self.style.SUCCESS("\nSeed data created."))
        self.stdout.write("Login credentials:")
        self.stdout.write("  Admin:      admin@acme.test     / Admin@12345")
        self.stdout.write("  Auditor:    auditor@acme.test   / Auditor@12345")
        self.stdout.write("  Department: dept@acme.test      / Dept@12345")

    # ----- creation helpers ----------------------------------------------
    def _create_company(self) -> Company:
        company, created = Company.objects.get_or_create(
            code="ACME",
            defaults={
                "name": "Acme Corp",
                "industry": "Manufacturing",
                "address": "100 Industrial Way, Springfield",
                "contact_email": "info@acme.test",
            },
        )
        self.stdout.write(("✓ created " if created else "↻ existing ") + f"company: {company.name}")
        return company

    def _create_departments(self, company: Company) -> dict[str, Department]:
        out = {}
        for name, code in [("Finance", "FIN"), ("IT", "IT"), ("HR", "HR")]:
            dep, created = Department.objects.get_or_create(
                company=company, name=name,
                defaults={"code": code, "description": f"{name} Department"},
            )
            out[name] = dep
            self.stdout.write(("✓ created " if created else "↻ existing ") + f"department: {name}")
        return out

    def _create_user(
        self, email, password, role, first, last, company, department
    ) -> User:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first,
                "last_name": last,
                "role": role,
                "company": company,
                "department": department,
                "is_active": True,
            },
        )
        if created:
            user.set_password(password)
            user.save()
        self.stdout.write(("✓ created " if created else "↻ existing ") + f"user: {email} ({role})")
        return user

    def _create_template(self, company: Company) -> TaskTemplate:
        template, created = TaskTemplate.objects.get_or_create(
            company=company, name="Quarterly Policy Acknowledgement", version=1,
            defaults={
                "description": "Quarterly check that policies are acknowledged.",
                "schema": {
                    "fields": [
                        {"key": "policy_id", "type": "text", "label": "Policy ID", "required": True},
                        {"key": "acknowledged_on", "type": "date", "label": "Acknowledged on", "required": True},
                        {"key": "category", "type": "dropdown", "label": "Category",
                         "options": ["Security", "HR", "Finance", "Operations"]},
                        {"key": "evidence", "type": "file_upload", "label": "Upload signed PDF"},
                    ]
                },
            },
        )
        self.stdout.write(("✓ created " if created else "↻ existing ") + f"template: {template.name}")
        return template

    def _create_audit(self, company, depts, lead_auditor) -> Audit:
        audit, created = Audit.objects.get_or_create(
            company=company, title="Q4 2026 Internal Compliance Audit",
            defaults={
                "description": "Quarterly internal compliance audit covering all departments.",
                "audit_type": AuditType.INTERNAL,
                "risk_level": RiskLevel.MEDIUM,
                "scheduled_start": date.today(),
                "scheduled_end": date.today() + timedelta(days=30),
                "lead_auditor": lead_auditor,
                "status": AuditStatus.ACTIVE,
                "actual_start": date.today(),
            },
        )
        if created:
            audit.departments.set(depts.values())
            audit.auditors.add(lead_auditor)
        self.stdout.write(("✓ created " if created else "↻ existing ") + f"audit: {audit.title}")
        return audit

    def _create_tasks(self, audit, depts, dept_user, template) -> None:
        defs = [
            ("Submit Q4 financial controls evidence", "Finance", TaskType.DOCUMENT_UPLOAD,
             Priority.HIGH, RiskLevel.HIGH, TaskStatus.IN_PROGRESS, 7),
            ("Review IT access control logs", "IT", TaskType.CHECKLIST,
             Priority.HIGH, RiskLevel.HIGH, TaskStatus.ASSIGNED, 14),
            ("HR policy acknowledgement evidence", "HR", TaskType.POLICY_ACK,
             Priority.NORMAL, RiskLevel.MEDIUM, TaskStatus.SUBMITTED, 3),
            ("Physical inspection of server room", "IT", TaskType.PHYSICAL,
             Priority.NORMAL, RiskLevel.MEDIUM, TaskStatus.ASSIGNED, 21),
            ("Reconciliation of vendor invoices", "Finance", TaskType.EVIDENCE,
             Priority.NORMAL, RiskLevel.LOW, TaskStatus.UNDER_REVIEW, 10),
        ]
        for title, dep_name, ttype, pri, risk, status, due_days in defs:
            task, created = Task.objects.get_or_create(
                audit=audit, title=title,
                defaults={
                    "description": "Auto-generated by seed_data.",
                    "task_type": ttype,
                    "priority": pri,
                    "risk_level": risk,
                    "department": depts[dep_name],
                    "assigned_to": dept_user if dep_name == "Finance" else None,
                    "due_date": date.today() + timedelta(days=due_days),
                    "status": status,
                    "template": template,
                    "created_by": audit.lead_auditor,
                },
            )
            self.stdout.write(("✓ created " if created else "↻ existing ") + f"task: {title}")
