"""AI verification orchestration.

The verification flow is:

  1. Extract text from the evidence file
  2. Run lightweight rule checks (presence, expiry date, completeness)
  3. Compute a confidence score
  4. Persist an ``AIExtractionResult`` and surface to the auditor

Auditors **always** make the final approval call (see ``apps.reviews``).
"""
from __future__ import annotations

import logging
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from apps.core.enums import AIVerificationResult

from .extractors import extract_text
from .models import AIExtractionResult

logger = logging.getLogger(__name__)

DATE_PATTERNS = (
    r"\b(\d{4}-\d{2}-\d{2})\b",
    r"\b(\d{2}/\d{2}/\d{4})\b",
)


def verify_evidence(evidence) -> AIExtractionResult:
    """Run the verification pipeline against an EvidenceFile."""
    text = extract_text(evidence.file.path)

    # Field heuristics
    fields: dict[str, Any] = {
        "char_count": len(text),
        "has_signature": bool(re.search(r"signature|signed by", text, re.I)),
        "has_dates": _find_dates(text),
    }

    # Rule evaluation
    expired, reason = _is_expired(fields["has_dates"])
    completeness = min(100, fields["char_count"] / 20)  # naive

    if fields["char_count"] == 0:
        result = AIVerificationResult.INCONCLUSIVE
        confidence = Decimal("0")
        notes = "No text could be extracted."
    elif expired:
        result = AIVerificationResult.FAIL
        confidence = Decimal("80")
        notes = f"Expired: {reason}"
    elif completeness < 30:
        result = AIVerificationResult.REQUIRES_HUMAN
        confidence = Decimal("40")
        notes = "Document appears too short / incomplete."
    else:
        result = AIVerificationResult.PASS
        confidence = Decimal(str(round(min(95, completeness), 2)))
        notes = "Initial checks passed.  Auditor must confirm."

    instance, _ = AIExtractionResult.objects.update_or_create(
        evidence=evidence,
        defaults={
            "extracted_text": text[:50_000],
            "fields": fields,
            "confidence": confidence,
            "result": result,
            "notes": notes,
        },
    )
    return instance


def _find_dates(text: str) -> list[str]:
    out: list[str] = []
    for pat in DATE_PATTERNS:
        out.extend(re.findall(pat, text))
    return out[:20]


def _is_expired(date_strings: list[str]) -> tuple[bool, str]:
    today = date.today()
    for s in date_strings:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                d = datetime.strptime(s, fmt).date()
            except ValueError:
                continue
            if d < today and (today - d).days > 365 * 5:
                # Treat very old documents as expired.  Real rules live in
                # the template's validation_rules; phase-10 wires it up.
                return True, f"Date {s} is older than 5 years"
            break
    return False, ""
