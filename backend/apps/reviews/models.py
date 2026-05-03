"""Auditor review, findings, and corrective actions."""
from __future__ import annotations

from django.db import models

from apps.core.enums import (
    CorrectiveActionStatus,
    FindingSeverity,
    Priority,
)
from apps.core.models import BaseModel


class Review(BaseModel):
    """Per-task auditor review record."""

    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    reviewer = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="reviews",
    )
    decision = models.CharField(
        max_length=20,
        choices=[("approve", "Approve"), ("reject", "Reject"),
                 ("pending", "Pending")],
        default="pending",
    )
    score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="0-100 review score",
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)


class Finding(BaseModel):
    """An issue identified during an audit."""

    audit = models.ForeignKey(
        "audits.Audit",
        on_delete=models.CASCADE,
        related_name="findings",
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="findings",
    )
    raised_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="raised_findings",
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=FindingSeverity.choices,
        default=FindingSeverity.MINOR,
    )

    class Meta:
        ordering = ("-created_at",)


class CorrectiveAction(BaseModel):
    """Action assigned to remediate a finding."""

    finding = models.ForeignKey(
        Finding,
        on_delete=models.CASCADE,
        related_name="corrective_actions",
    )
    assigned_to = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="corrective_actions",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=CorrectiveActionStatus.choices,
        default=CorrectiveActionStatus.OPEN,
    )
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
