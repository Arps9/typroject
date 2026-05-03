"""Centralised DRF exception handler.

Wraps every error response in the standard envelope used across the API.
"""
from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Return a uniform error envelope for DRF + Django exceptions."""
    # Translate Django exceptions to DRF
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled - log and produce 500
        logger.exception("Unhandled API exception", extra={"context": context})
        return Response(
            {
                "success": False,
                "data": None,
                "message": "Internal server error",
                "errors": [{"detail": "An unexpected error occurred."}],
            },
            status=500,
        )

    detail = response.data
    message = "Request failed"
    errors: Any = detail

    if isinstance(detail, dict):
        message = str(detail.get("detail", message))
        if "detail" in detail and len(detail) == 1:
            errors = [{"detail": message}]
        else:
            errors = detail
    elif isinstance(detail, list):
        errors = [{"detail": str(item)} for item in detail]

    response.data = {
        "success": False,
        "data": None,
        "message": message,
        "errors": errors,
    }
    return response
