"""Project-wide enums.

Centralising these prevents magic strings from drifting across apps.
"""
from __future__ import annotations

from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Administrator"
    AUDITOR = "auditor", "Auditor"
    DEPARTMENT = "department", "Department User"


class AuditStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    ACTIVE = "active", "Active"
    REVIEWING = "reviewing", "Under Review"
    CLOSED = "closed", "Closed"
    CANCELLED = "cancelled", "Cancelled"


class AuditType(models.TextChoices):
    INTERNAL = "internal", "Internal"
    EXTERNAL = "external", "External"
    REGULATORY = "regulatory", "Regulatory"
    PHYSICAL = "physical", "Physical Inspection"


class TaskType(models.TextChoices):
    DOCUMENT_UPLOAD = "document_upload", "Document Upload"
    CHECKLIST = "checklist", "Checklist"
    POLICY_ACK = "policy_ack", "Policy Acknowledgement"
    EVIDENCE = "evidence", "Evidence Collection"
    PHYSICAL = "physical", "Physical Inspection"
    CORRECTIVE = "corrective", "Corrective Action"


class TaskStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ASSIGNED = "assigned", "Assigned"
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CLOSED = "closed", "Closed"
    OVERDUE = "overdue", "Overdue"


class RiskLevel(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class Priority(models.TextChoices):
    LOW = "low", "Low"
    NORMAL = "normal", "Normal"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class FindingSeverity(models.TextChoices):
    OBSERVATION = "observation", "Observation"
    MINOR = "minor", "Minor"
    MAJOR = "major", "Major"
    CRITICAL = "critical", "Critical"


class CorrectiveActionStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    VERIFIED = "verified", "Verified"
    CLOSED = "closed", "Closed"


class AIVerificationResult(models.TextChoices):
    PASS = "pass", "Pass"
    FAIL = "fail", "Fail"
    INCONCLUSIVE = "inconclusive", "Inconclusive"
    REQUIRES_HUMAN = "requires_human", "Requires Human Review"


class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    IN_APP = "in_app", "In App"
    BOTH = "both", "Both"
