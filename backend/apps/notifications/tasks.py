"""Periodic notification tasks."""
from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.core.enums import TaskStatus

logger = logging.getLogger(__name__)


@shared_task(name="apps.notifications.tasks.dispatch_daily_reminders")
def dispatch_daily_reminders() -> int:
    """Send a reminder to assignees of tasks due in <= 3 days."""
    from apps.tasks.models import Task

    from .services import notify

    horizon = timezone.now().date() + timedelta(days=3)
    qs = Task.objects.filter(
        due_date__lte=horizon,
        assigned_to__isnull=False,
    ).exclude(status__in=[
        TaskStatus.APPROVED, TaskStatus.CLOSED, TaskStatus.REJECTED,
    ]).select_related("assigned_to")

    count = 0
    for t in qs:
        notify(
            t.assigned_to,
            title=f"Task '{t.title}' is due {t.due_date}",
            body="Please submit evidence and mark the task as complete.",
            link=f"/tasks/{t.id}",
        )
        count += 1
    logger.info("Dispatched %s reminders", count)
    return count
