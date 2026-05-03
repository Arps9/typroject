from __future__ import annotations

from rest_framework import serializers

from apps.users.serializers import UserMiniSerializer

from .models import Audit


class AuditListSerializer(serializers.ModelSerializer):
    lead_auditor_detail = UserMiniSerializer(source="lead_auditor", read_only=True)
    department_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Audit
        fields = (
            "id", "title", "audit_type", "risk_level", "status",
            "scheduled_start", "scheduled_end",
            "actual_start", "actual_end",
            "lead_auditor", "lead_auditor_detail",
            "department_count", "task_count",
            "compliance_score",
            "created_at", "updated_at",
        )

    def get_department_count(self, obj) -> int:
        return obj.departments.count()

    def get_task_count(self, obj) -> int:
        return obj.tasks.count()


class AuditDetailSerializer(serializers.ModelSerializer):
    lead_auditor_detail = UserMiniSerializer(source="lead_auditor", read_only=True)
    auditors_detail = UserMiniSerializer(source="auditors", many=True, read_only=True)

    class Meta:
        model = Audit
        fields = (
            "id", "company", "title", "description",
            "audit_type", "risk_level",
            "departments", "scheduled_start", "scheduled_end",
            "actual_start", "actual_end",
            "lead_auditor", "lead_auditor_detail",
            "auditors", "auditors_detail",
            "status", "compliance_score", "summary",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "compliance_score")

    def validate(self, data):
        start = data.get("scheduled_start", getattr(self.instance, "scheduled_start", None))
        end = data.get("scheduled_end", getattr(self.instance, "scheduled_end", None))
        if start and end and end < start:
            raise serializers.ValidationError(
                {"scheduled_end": "scheduled_end must be on or after scheduled_start"}
            )
        return data
