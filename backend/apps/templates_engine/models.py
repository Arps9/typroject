"""Dynamic compliance template engine.

A TaskTemplate stores a JSON schema describing the fields a department user
must fill in.  Field types supported (Phase 7): text, number, date, dropdown,
checkbox, file_upload, with optional ``conditional`` rules.

Schema example:

    {
      "fields": [
        {"key": "policy_id", "type": "text", "label": "Policy ID", "required": true},
        {"key": "expires_on", "type": "date", "label": "Expiry"},
        {"key": "category", "type": "dropdown", "label": "Category",
         "options": ["A", "B", "C"]},
        {"key": "evidence", "type": "file_upload", "label": "Upload PDF"}
      ]
    }
"""
from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class TaskTemplate(BaseModel):
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="templates",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    schema = models.JSONField(
        default=dict,
        help_text="Field schema definition (see module docstring)",
    )
    validation_rules = models.JSONField(
        default=dict, blank=True,
        help_text="Optional rule expressions for AI verification",
    )

    class Meta:
        ordering = ("name", "-version")
        unique_together = (("company", "name", "version"),)

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"
