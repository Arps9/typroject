from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class Department(BaseModel):
    """A department within a company (Finance, IT, HR, ...)."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="departments",
    )
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
    )

    class Meta:
        unique_together = (("company", "name"),)
        ordering = ("company", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.company.code if self.company else '-'})"
