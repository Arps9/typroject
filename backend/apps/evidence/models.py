"""Evidence file storage."""
from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


def _upload_path(instance: "EvidenceFile", filename: str) -> str:
    return f"evidence/{instance.task_id}/{filename}"


class EvidenceFile(BaseModel):
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="evidence_files",
    )
    uploaded_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_evidence",
    )

    file = models.FileField(upload_to=_upload_path, max_length=512)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    checksum_sha256 = models.CharField(max_length=64, blank=True)

    # Populated by AI extraction pipeline
    extracted_text = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["task", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.original_filename
