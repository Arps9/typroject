"""Standard API response envelope.

Every successful API response is wrapped as::

    {
        "success": true,
        "data": <payload>,
        "message": "OK",
        "errors": null
    }

Error responses are produced by ``apps.core.exceptions.api_exception_handler``.
"""
from __future__ import annotations

from typing import Any

from rest_framework.response import Response


def envelope(
    data: Any = None,
    message: str = "OK",
    *,
    status: int = 200,
    errors: Any = None,
    success: bool | None = None,
) -> Response:
    """Build a standard API response envelope."""
    if success is None:
        success = 200 <= status < 400
    return Response(
        {
            "success": success,
            "data": data,
            "message": message,
            "errors": errors,
        },
        status=status,
    )
