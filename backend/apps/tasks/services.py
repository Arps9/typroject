"""Task workflow service.

Centralises status transitions so views and Celery beat agree on the rules.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from apps.core.enums import TaskStatus

if TYPE_CHECKING:
    from .models import Task


class TaskTransitionError(Exception):
    pass


_TRANSITIONS: dict[str, set[str]] = {
    TaskStatus.DRAFT: {TaskStatus.ASSIGNED},
    TaskStatus.ASSIGNED: {TaskStatus.IN_PROGRESS, TaskStatus.DRAFT},
    TaskStatus.IN_PROGRESS: {TaskStatus.SUBMITTED, TaskStatus.ASSIGNED},
    TaskStatus.SUBMITTED: {TaskStatus.UNDER_REVIEW},
    TaskStatus.UNDER_REVIEW: {TaskStatus.APPROVED, TaskStatus.REJECTED},
    TaskStatus.APPROVED: {TaskStatus.CLOSED},
    TaskStatus.REJECTED: {TaskStatus.IN_PROGRESS},
    TaskStatus.CLOSED: set(),
    TaskStatus.OVERDUE: {TaskStatus.IN_PROGRESS, TaskStatus.SUBMITTED},
}


@transaction.atomic
def transition_task(task: "Task", target: str, *, by=None) -> "Task":
    allowed = _TRANSITIONS.get(task.status, set())
    if target not in allowed:
        raise TaskTransitionError(
            f"Cannot transition from '{task.status}' to '{target}'."
            f" Allowed: {sorted(allowed) or 'none'}."
        )
    task.status = target
    if target == TaskStatus.SUBMITTED:
        task.submitted_at = timezone.now()
    if target in {TaskStatus.APPROVED, TaskStatus.REJECTED}:
        task.reviewed_at = timezone.now()
    task.save()
    return task


def assign_task(task: "Task", user) -> "Task":
    """Assign and (if needed) bump status from DRAFT to ASSIGNED."""
    task.assigned_to = user
    if task.status == TaskStatus.DRAFT:
        task.status = TaskStatus.ASSIGNED
    task.save()
    return task
