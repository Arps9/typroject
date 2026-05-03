"""Notifications and audit log models."""
from __future__ import annotations

from django.db import models

from apps.core.enums import NotificationChannel
from apps.core.models import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    channel = models.CharField(
        max_length=10,
        choices=NotificationChannel.choices,
        default=NotificationChannel.IN_APP,
    )
    link = models.CharField(max_length=512, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "read_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.title}"


class AuditLog(BaseModel):
    """Append-only log written by the AuditLogMiddleware."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_log_entries",
    )
    action = models.CharField(max_length=20)  # POST/PUT/PATCH/DELETE
    path = models.CharField(max_length=255)
    status_code = models.PositiveSmallIntegerField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]
