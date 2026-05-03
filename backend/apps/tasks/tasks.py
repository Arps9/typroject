"""Celery tasks for the Tasks module (yes, naming is awkward)."""
from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.core.enums import TaskStatus

logger = logging.getLogger(__name__)


@shared_task(name="apps.tasks.tasks.mark_overdue_tasks")
def mark_overdue_tasks() -> int:
    """Sweep tasks whose due date has passed and stamp them OVERDUE.

    Excludes tasks already in a terminal state.  Returns the number updated.
    """
    from .models import Task

    today = timezone.now().date()
    qs = Task.objects.filter(due_date__lt=today).exclude(
        status__in=[
            TaskStatus.APPROVED,
            TaskStatus.CLOSED,
            TaskStatus.OVERDUE,
            TaskStatus.REJECTED,
        ]
    )
    updated = qs.update(status=TaskStatus.OVERDUE)
    logger.info("Marked %s tasks as overdue", updated)
    return updated
