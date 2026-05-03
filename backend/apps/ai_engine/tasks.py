"""Celery tasks for AI verification."""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="apps.ai_engine.tasks.verify_evidence_async")
def verify_evidence_async(evidence_id: str) -> dict:
    """Run the AI verification pipeline against an evidence file."""
    from apps.evidence.models import EvidenceFile

    from .services import verify_evidence

    try:
        evidence = EvidenceFile.objects.get(pk=evidence_id)
    except EvidenceFile.DoesNotExist:
        logger.warning("Evidence %s not found for AI verification", evidence_id)
        return {"ok": False, "reason": "not_found"}

    result = verify_evidence(evidence)
    return {
        "ok": True,
        "result": result.result,
        "confidence": str(result.confidence),
    }
