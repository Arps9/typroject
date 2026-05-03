"""Compliance task models.

Each Audit contains many Tasks.  A Task lives through the lifecycle:

    DRAFT -> ASSIGNED -> IN_PROGRESS -> SUBMITTED -> UNDER_REVIEW
                                                     |-> APPROVED -> CLOSED
                                                     |-> REJECTED -> IN_PROGRESS
                              (any non-final) ----> OVERDUE (system-set)
"""
from __future__ import annotations

from django.db import models
from django.utils import timezone

from apps.core.enums import Priority, RiskLevel, TaskStatus, TaskType
from apps.core.models import BaseModel


class Task(BaseModel):
    audit = models.ForeignKey(
        "audits.Audit",
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.DOCUMENT_UPLOAD,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        help_text="Drives whether AI can pre-validate or human review is required",
    )

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="tasks",
    )
    assigned_to = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
    )

    template = models.ForeignKey(
        "templates_engine.TaskTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    due_date = models.DateField(null=True, blank=True, db_index=True)

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.DRAFT,
        db_index=True,
    )

    # Form payload submitted by the department user, validated against the
    # template's schema.  Stored as JSONB for flexibility.
    submission_data = models.JSONField(default=dict, blank=True)

    # Tracking
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("due_date", "-created_at")
        indexes = [
            models.Index(fields=["audit", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["department", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"

    # ------------------------------------------------------------------
    @property
    def is_overdue(self) -> bool:
        if not self.due_date or self.status in {
            TaskStatus.APPROVED, TaskStatus.CLOSED, TaskStatus.REJECTED
        }:
            return False
        return self.due_date < timezone.now().date()
