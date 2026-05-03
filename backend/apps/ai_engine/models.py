"""AI extraction & verification result records."""
from __future__ import annotations

from django.db import models

from apps.core.enums import AIVerificationResult
from apps.core.models import BaseModel


class AIExtractionResult(BaseModel):
    """One result row per evidence file processed by the AI pipeline.

    The auditor always sees these as *suggestions*; the workflow does not
    auto-approve based on AI output (see ``apps.reviews``).
    """

    evidence = models.OneToOneField(
        "evidence.EvidenceFile",
        on_delete=models.CASCADE,
        related_name="ai_result",
    )

    extracted_text = models.TextField(blank=True)
    fields = models.JSONField(default=dict, blank=True)

    confidence = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0,
        help_text="0-100 confidence score",
    )
    result = models.CharField(
        max_length=20,
        choices=AIVerificationResult.choices,
        default=AIVerificationResult.INCONCLUSIVE,
    )
    notes = models.TextField(blank=True)
    raw_engine_output = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"AIResult({self.evidence_id}, {self.result})"
