"""Audit-log middleware.

Records every authenticated, mutating API request.  Read-only requests are
ignored to keep the table small and queryable.
"""
from __future__ import annotations

import json
import logging

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("apps.audit_log")

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditLogMiddleware(MiddlewareMixin):
    """Persist a row in ``apps.notifications.AuditLog`` for every write."""

    def process_response(self, request, response):
        try:
            if request.method not in WRITE_METHODS:
                return response

            user = getattr(request, "user", None)
            if not user or not user.is_authenticated:
                return response

            # Avoid logging admin app and static
            path = request.path
            if path.startswith(("/admin/", "/static/", "/media/")):
                return response

            from apps.notifications.models import AuditLog  # local import - avoid cycles

            AuditLog.objects.create(
                user=user,
                action=request.method,
                path=path[:255],
                status_code=response.status_code,
                metadata=_safe_metadata(request),
            )
        except Exception:  # pragma: no cover - never break the response
            logger.exception("Failed to write audit log")
        return response


def _safe_metadata(request) -> dict:
    """Capture a small metadata blob.  Avoid PII / huge bodies."""
    return {
        "ip": _client_ip(request),
        "ua": request.META.get("HTTP_USER_AGENT", "")[:200],
        "query": dict(request.GET.lists())[:10] if False else dict(request.GET.items()),
    }


def _client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")
