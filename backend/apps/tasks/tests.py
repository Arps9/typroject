"""Task workflow tests."""
from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model

from apps.audits.models import Audit
from apps.companies.models import Company
from apps.core.enums import TaskStatus, UserRole
from apps.departments.models import Department
from apps.tasks.models import Task
from apps.tasks.services import TaskTransitionError, transition_task

User = get_user_model()


@pytest.fixture
def setup(db):
    company = Company.objects.create(name="Test Co", code="TST")
    department = Department.objects.create(company=company, name="Test Dept")
    auditor = User.objects.create_user(
        email="auditor@test.local", password="pw", role=UserRole.AUDITOR,
        company=company,
    )
    audit = Audit.objects.create(
        company=company, title="A", scheduled_start=date.today(),
        scheduled_end=date.today() + timedelta(days=5), lead_auditor=auditor,
    )
    return company, department, auditor, audit


@pytest.fixture
def task(setup):
    _, dep, auditor, audit = setup
    return Task.objects.create(
        audit=audit, department=dep, title="Test task", created_by=auditor,
    )


def test_default_status_is_draft(task):
    assert task.status == TaskStatus.DRAFT


def test_full_happy_path(task):
    transition_task(task, TaskStatus.ASSIGNED)
    transition_task(task, TaskStatus.IN_PROGRESS)
    transition_task(task, TaskStatus.SUBMITTED)
    transition_task(task, TaskStatus.UNDER_REVIEW)
    transition_task(task, TaskStatus.APPROVED)
    transition_task(task, TaskStatus.CLOSED)
    assert task.status == TaskStatus.CLOSED


def test_rejected_returns_to_in_progress(task):
    transition_task(task, TaskStatus.ASSIGNED)
    transition_task(task, TaskStatus.IN_PROGRESS)
    transition_task(task, TaskStatus.SUBMITTED)
    transition_task(task, TaskStatus.UNDER_REVIEW)
    transition_task(task, TaskStatus.REJECTED)
    transition_task(task, TaskStatus.IN_PROGRESS)
    assert task.status == TaskStatus.IN_PROGRESS


def test_cannot_skip_steps(task):
    with pytest.raises(TaskTransitionError):
        transition_task(task, TaskStatus.APPROVED)
