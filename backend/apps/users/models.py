"""Custom user model with role-based access control."""
from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.core.enums import UserRole
from apps.core.models import SoftDeleteManager, SoftDeleteMixin, TimeStampedMixin

from .managers import UserManager


class User(SoftDeleteMixin, TimeStampedMixin, AbstractBaseUser, PermissionsMixin):
    """Application user.

    Users authenticate by email.  Each user has exactly one ``role`` and may
    optionally belong to a ``department`` (department users) and a
    ``company`` (everyone except superuser).
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=32, blank=True)

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.DEPARTMENT,
        db_index=True,
    )

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("email",)
        indexes = [
            models.Index(fields=["role", "company"]),
            models.Index(fields=["company", "department"]),
        ]

    # ------------------------------------------------------------------ helpers
    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_auditor(self) -> bool:
        return self.role == UserRole.AUDITOR

    @property
    def is_department_user(self) -> bool:
        return self.role == UserRole.DEPARTMENT
