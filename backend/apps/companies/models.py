"""Company (tenant) model."""
from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class Company(BaseModel):
    """Top-level tenant.

    Departments and users belong to a company.  In the current design we run
    in single-tenant mode (one company per deployment) but the schema is
    multi-tenant ready.
    """

    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Short code for reports")
    industry = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    logo_url = models.URLField(blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self) -> str:
        return self.name
