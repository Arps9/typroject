"""Reusable model mixins.

Every domain entity inherits from ``BaseModel`` to get UUID primary keys,
created/updated timestamps, and soft-delete support out of the box.
"""
from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone


class TimeStampedMixin(models.Model):
    """Adds created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDPrimaryKeyMixin(models.Model):
    """Uses a UUID4 as the primary key (safer to expose in URLs)."""

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self) -> "SoftDeleteQuerySet":
        return self.filter(deleted_at__isnull=True)

    def dead(self) -> "SoftDeleteQuerySet":
        return self.exclude(deleted_at__isnull=True)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Default manager that hides soft-deleted rows."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return super().get_queryset().alive()


class SoftDeleteMixin(models.Model):
    """Adds soft-delete support via a ``deleted_at`` column."""

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents: bool = False) -> tuple:  # type: ignore[override]
        """Soft delete: stamp ``deleted_at`` instead of removing the row."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
        return (1, {self._meta.label: 1})

    def hard_delete(self, using=None, keep_parents: bool = False) -> tuple:
        return super().delete(using=using, keep_parents=keep_parents)


class BaseModel(UUIDPrimaryKeyMixin, TimeStampedMixin, SoftDeleteMixin):
    """The base every domain model should inherit from."""

    class Meta:
        abstract = True
        ordering = ("-created_at",)
