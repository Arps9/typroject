"""Audit service layer.

Encapsulates state transitions and score calculation so views stay thin.
"""
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from apps.core.enums import AuditStatus, TaskStatus

if TYPE_CHECKING:
    from .models import Audit


class AuditTransitionError(Exception):
    """Raised when an audit cannot transition to a given status."""


# Allowed transitions adjacency list
_TRANSITIONS = {
    AuditStatus.SCHEDULED: {AuditStatus.ACTIVE, AuditStatus.CANCELLED},
    AuditStatus.ACTIVE: {AuditStatus.REVIEWING, AuditStatus.CANCELLED},
    AuditStatus.REVIEWING: {AuditStatus.CLOSED, AuditStatus.ACTIVE},
    AuditStatus.CLOSED: set(),
    AuditStatus.CANCELLED: set(),
}


@transaction.atomic
def transition_audit(audit: "Audit", target_status: str) -> "Audit":
    """Move ``audit`` into ``target_status`` if the transition is valid."""
    current = audit.status
    allowed = _TRANSITIONS.get(current, set())
    if target_status not in allowed:
        raise AuditTransitionError(
            f"Cannot transition from '{current}' to '{target_status}'. "
            f"Allowed: {sorted(allowed) or 'none'}."
        )

    audit.status = target_status

    if target_status == AuditStatus.ACTIVE and not audit.actual_start:
        audit.actual_start = timezone.now().date()

    if target_status == AuditStatus.CLOSED:
        audit.actual_end = timezone.now().date()
        audit.compliance_score = compute_compliance_score(audit)

    audit.save()
    return audit


def compute_compliance_score(audit: "Audit") -> Decimal:
    """Simple weighted score: approved / non-draft tasks * 100.

    Replaceable with a richer rule-engine in a later phase.
    """
    qs = audit.tasks.exclude(status=TaskStatus.DRAFT)
    total = qs.count()
    if total == 0:
        return Decimal("0.00")

    approved = qs.filter(status=TaskStatus.APPROVED).count()
    return (Decimal(approved) / Decimal(total) * Decimal("100")).quantize(Decimal("0.01"))
