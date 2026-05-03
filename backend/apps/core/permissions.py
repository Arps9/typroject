"""Role-based DRF permissions.

Use these as ``permission_classes`` on viewsets to restrict access by role.
"""
from __future__ import annotations

from rest_framework import permissions

from apps.core.enums import UserRole


class IsAuthenticatedAndActive(permissions.BasePermission):
    """Authenticated and not soft-deleted."""

    def has_permission(self, request, view) -> bool:
        u = request.user
        return bool(u and u.is_authenticated and u.is_active and not getattr(u, "deleted_at", None))


class _RoleRequiredMixin:
    role: str = ""

    def has_permission(self, request, view) -> bool:
        u = request.user
        return bool(
            u and u.is_authenticated and u.is_active
            and getattr(u, "role", None) == self.role
        )


class IsAdmin(_RoleRequiredMixin, permissions.BasePermission):
    role = UserRole.ADMIN


class IsAuditor(_RoleRequiredMixin, permissions.BasePermission):
    role = UserRole.AUDITOR


class IsDepartmentUser(_RoleRequiredMixin, permissions.BasePermission):
    role = UserRole.DEPARTMENT


class IsAdminOrAuditor(permissions.BasePermission):
    """Allowed for both admins and auditors."""

    def has_permission(self, request, view) -> bool:
        u = request.user
        return bool(
            u and u.is_authenticated and u.is_active
            and getattr(u, "role", None) in {UserRole.ADMIN, UserRole.AUDITOR}
        )


class ReadOnlyOrIsAdmin(permissions.BasePermission):
    """SAFE methods open to any authenticated user, writes admin-only."""

    def has_permission(self, request, view) -> bool:
        u = request.user
        if not (u and u.is_authenticated and u.is_active):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(u, "role", None) == UserRole.ADMIN


class IsOwnerOrAdmin(permissions.BasePermission):
    """Object-level permission: owner can read/write, admin can do anything.

    The view must set ``owner_field`` to the FK attribute name (default
    ``"assigned_to"``).
    """

    def has_object_permission(self, request, view, obj) -> bool:
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if getattr(u, "role", None) == UserRole.ADMIN:
            return True
        owner_field = getattr(view, "owner_field", "assigned_to")
        return getattr(obj, owner_field, None) == u
