"""Report generation.

A minimal PDF and CSV generator suitable for the MVP.  Phase 13 will replace
this with branded WeasyPrint templates and full audit/finding/CA sections.
"""
from __future__ import annotations

import csv
import io
from typing import Iterable

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from apps.audits.models import Audit


def audit_summary_pdf(audit: Audit) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, title=f"Audit {audit.title}")
    styles = getSampleStyleSheet()

    story = [
        Paragraph(f"<b>Audit Report:</b> {audit.title}", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"<b>Status:</b> {audit.status}", styles["Normal"]),
        Paragraph(f"<b>Type:</b> {audit.audit_type}", styles["Normal"]),
        Paragraph(f"<b>Risk:</b> {audit.risk_level}", styles["Normal"]),
        Paragraph(
            f"<b>Period:</b> {audit.scheduled_start} → {audit.scheduled_end}",
            styles["Normal"],
        ),
        Paragraph(
            f"<b>Compliance score:</b> {audit.compliance_score or 'pending'}",
            styles["Normal"],
        ),
        Spacer(1, 18),
        Paragraph("<b>Tasks</b>", styles["Heading2"]),
    ]

    rows = [["Title", "Status", "Department", "Assignee", "Due"]]
    for t in audit.tasks.select_related("department", "assigned_to")[:200]:
        rows.append([
            t.title,
            t.status,
            t.department.name if t.department else "",
            t.assigned_to.email if t.assigned_to else "—",
            str(t.due_date or "—"),
        ])
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
    ]))
    story.append(table)

    doc.build(story)
    return buf.getvalue()


def audit_tasks_csv(audit: Audit) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "task_id", "title", "status", "task_type", "priority",
        "risk_level", "department", "assignee", "due_date", "submitted_at",
    ])
    for t in audit.tasks.select_related("department", "assigned_to"):
        writer.writerow([
            str(t.id), t.title, t.status, t.task_type, t.priority,
            t.risk_level,
            t.department.name if t.department else "",
            t.assigned_to.email if t.assigned_to else "",
            t.due_date or "", t.submitted_at or "",
        ])
    return buf.getvalue().encode("utf-8")
