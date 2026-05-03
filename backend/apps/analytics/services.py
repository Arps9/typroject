"""Aggregation queries used by the dashboards."""
from __future__ import annotations

from typing import Any

from django.db.models import Avg, Count, Q

from apps.audits.models import Audit
from apps.core.enums import AuditStatus, RiskLevel, TaskStatus
from apps.departments.models import Department
from apps.tasks.models import Task


# ---------------------------------------------------------------------------
# Admin / company-wide
# ---------------------------------------------------------------------------
def admin_dashboard(company_id) -> dict[str, Any]:
    audits = Audit.objects.filter(company_id=company_id) if company_id else Audit.objects.all()
    tasks = Task.objects.filter(audit__company_id=company_id) if company_id else Task.objects.all()

    return {
        "summary": {
            "total_audits": audits.count(),
            "active_audits": audits.filter(status=AuditStatus.ACTIVE).count(),
            "scheduled_audits": audits.filter(status=AuditStatus.SCHEDULED).count(),
            "closed_audits": audits.filter(status=AuditStatus.CLOSED).count(),
            "total_tasks": tasks.count(),
            "approved_tasks": tasks.filter(status=TaskStatus.APPROVED).count(),
            "overdue_tasks": tasks.filter(status=TaskStatus.OVERDUE).count(),
            "average_compliance_score": float(
                audits.filter(compliance_score__isnull=False)
                .aggregate(v=Avg("compliance_score"))["v"] or 0
            ),
        },
        "tasks_by_status": _group_by(tasks, "status", TaskStatus),
        "audits_by_risk": _group_by(audits, "risk_level", RiskLevel),
        "department_compliance": _department_compliance(company_id),
    }


def auditor_dashboard(user) -> dict[str, Any]:
    audits = Audit.objects.filter(Q(lead_auditor=user) | Q(auditors=user)).distinct()
    tasks = Task.objects.filter(Q(audit__lead_auditor=user) | Q(audit__auditors=user)).distinct()
    review_queue = tasks.filter(status=TaskStatus.SUBMITTED).count() + \
        tasks.filter(status=TaskStatus.UNDER_REVIEW).count()

    return {
        "summary": {
            "my_audits": audits.count(),
            "active_audits": audits.filter(status=AuditStatus.ACTIVE).count(),
            "review_queue": review_queue,
            "approved_today": tasks.filter(status=TaskStatus.APPROVED).count(),
        },
        "tasks_by_status": _group_by(tasks, "status", TaskStatus),
    }


def department_dashboard(user) -> dict[str, Any]:
    if not user.department_id:
        return {"summary": {}, "tasks_by_status": []}

    tasks = Task.objects.filter(department_id=user.department_id)
    my_tasks = tasks.filter(assigned_to=user)

    return {
        "summary": {
            "my_open_tasks": my_tasks.exclude(status__in=[
                TaskStatus.APPROVED, TaskStatus.CLOSED, TaskStatus.REJECTED,
            ]).count(),
            "my_overdue_tasks": my_tasks.filter(status=TaskStatus.OVERDUE).count(),
            "department_total": tasks.count(),
            "department_compliance": _department_compliance_value(user.department_id),
        },
        "tasks_by_status": _group_by(my_tasks, "status", TaskStatus),
    }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _group_by(qs, field: str, choices) -> list[dict[str, Any]]:
    """Return [{label, value, count}] for a TextChoices field."""
    rows = qs.values(field).annotate(count=Count("id"))
    by_value = {r[field]: r["count"] for r in rows}
    out: list[dict[str, Any]] = []
    for value, label in choices.choices:
        out.append({"label": label, "value": value, "count": by_value.get(value, 0)})
    return out


def _department_compliance(company_id) -> list[dict[str, Any]]:
    deps = Department.objects.filter(company_id=company_id) if company_id else Department.objects.all()
    out: list[dict[str, Any]] = []
    for dep in deps:
        out.append({
            "department_id": str(dep.id),
            "department_name": dep.name,
            "score": _department_compliance_value(dep.id),
        })
    return out


def _department_compliance_value(department_id) -> float:
    qs = Task.objects.filter(department_id=department_id).exclude(status=TaskStatus.DRAFT)
    total = qs.count()
    if not total:
        return 0.0
    approved = qs.filter(status=TaskStatus.APPROVED).count()
    return round(approved / total * 100, 2)
