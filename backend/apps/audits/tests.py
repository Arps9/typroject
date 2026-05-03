"""Audit lifecycle tests."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.audits.models import Audit
from apps.audits.services import (
    AuditTransitionError,
    compute_compliance_score,
    transition_audit,
)
from apps.companies.models import Company
from apps.core.enums import AuditStatus, TaskStatus, UserRole
from apps.departments.models import Department
from apps.tasks.models import Task

User = get_user_model()


@pytest.fixture
def company(db):
    return Company.objects.create(name="Test Co", code="TST")


@pytest.fixture
def department(db, company):
    return Department.objects.create(company=company, name="Test Dept")


@pytest.fixture
def auditor(db, company):
    return User.objects.create_user(
        email="auditor@test.local",
        password="pw",
        role=UserRole.AUDITOR,
        company=company,
    )


@pytest.fixture
def audit(db, company, auditor, department):
    a = Audit.objects.create(
        company=company,
        title="Test Audit",
        scheduled_start=date.today(),
        scheduled_end=date.today() + timedelta(days=10),
        lead_auditor=auditor,
    )
    a.departments.add(department)
    return a


def test_initial_status_is_scheduled(audit):
    assert audit.status == AuditStatus.SCHEDULED


def test_valid_transition_scheduled_to_active(audit):
    transition_audit(audit, AuditStatus.ACTIVE)
    assert audit.status == AuditStatus.ACTIVE
    assert audit.actual_start == date.today()


def test_invalid_transition_raises(audit):
    with pytest.raises(AuditTransitionError):
        transition_audit(audit, AuditStatus.CLOSED)


def test_close_computes_score(audit, department):
    transition_audit(audit, AuditStatus.ACTIVE)
    Task.objects.create(
        audit=audit, title="t1", department=department,
        status=TaskStatus.APPROVED, due_date=date.today(),
    )
    Task.objects.create(
        audit=audit, title="t2", department=department,
        status=TaskStatus.REJECTED, due_date=date.today(),
    )
    transition_audit(audit, AuditStatus.REVIEWING)
    transition_audit(audit, AuditStatus.CLOSED)
    audit.refresh_from_db()
    assert audit.compliance_score == Decimal("50.00")
    assert audit.actual_end == date.today()


def test_compute_score_skips_drafts(audit, department):
    Task.objects.create(
        audit=audit, title="t1", department=department,
        status=TaskStatus.DRAFT, due_date=date.today(),
    )
    Task.objects.create(
        audit=audit, title="t2", department=department,
        status=TaskStatus.APPROVED, due_date=date.today(),
    )
    score = compute_compliance_score(audit)
    assert score == Decimal("100.00")
