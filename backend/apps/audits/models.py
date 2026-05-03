"""Audit lifecycle model.

An Audit groups a set of compliance Tasks under a defined scope, period
and lead auditor.  Statuses follow:

    SCHEDULED -> ACTIVE -> REVIEWING -> CLOSED
                                        \\-> CANCELLED
"""
from __future__ import annotations

from django.db import models

from apps.core.enums import AuditStatus, AuditType, RiskLevel
from apps.core.models import BaseModel


class Audit(BaseModel):
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="audits",
    )

    # Scope
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    audit_type = models.CharField(
        max_length=20,
        choices=AuditType.choices,
        default=AuditType.INTERNAL,
    )
    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.MEDIUM,
    )

    departments = models.ManyToManyField(
        "departments.Department",
        related_name="audits",
        blank=True,
    )

    # Schedule
    scheduled_start = models.DateField()
    scheduled_end = models.DateField()
    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)

    # People
    lead_auditor = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="lead_audits",
    )
    auditors = models.ManyToManyField(
        "users.User",
        related_name="participating_audits",
        blank=True,
    )

    # Lifecycle
    status = models.CharField(
        max_length=20,
        choices=AuditStatus.choices,
        default=AuditStatus.SCHEDULED,
        db_index=True,
    )

    # Outcome
    compliance_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="0-100 final compliance score after closure",
    )
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ("-scheduled_start", "title")
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["status", "scheduled_start"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"

    # ------------------------------------------------------------------ helpers
    @property
    def is_open(self) -> bool:
        return self.status in {
            AuditStatus.SCHEDULED,
            AuditStatus.ACTIVE,
            AuditStatus.REVIEWING,
        }
