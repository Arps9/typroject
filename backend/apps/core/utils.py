"""General-purpose helpers."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any


def serialize_value(value: Any) -> Any:
    """Make a value JSON-serialisable (used by analytics aggregations)."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "__str__"):
        return str(value)
    return value


def safe_get(obj: Any, attr: str, default: Any = None) -> Any:
    """Get attribute or key, returning ``default`` on failure."""
    try:
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return getattr(obj, attr, default)
    except Exception:
        return default
