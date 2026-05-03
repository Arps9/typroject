"""Celery configuration for the Compliance Audit project."""
from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "compliance_audit.settings.development"
)

app = Celery("compliance_audit")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# ---------------------------------------------------------------------------
# Periodic schedule
# ---------------------------------------------------------------------------
app.conf.beat_schedule = {
    "check-overdue-tasks-every-hour": {
        "task": "apps.tasks.tasks.mark_overdue_tasks",
        "schedule": crontab(minute=0),
    },
    "send-daily-reminders": {
        "task": "apps.notifications.tasks.dispatch_daily_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self) -> str:
    """Smoke-test task used during local development."""
    return f"Request: {self.request!r}"
