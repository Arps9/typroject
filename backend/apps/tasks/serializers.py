from rest_framework import serializers

from apps.users.serializers import UserMiniSerializer

from .models import Task


class TaskListSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserMiniSerializer(source="assigned_to", read_only=True)
    audit_title = serializers.CharField(source="audit.title", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id", "title", "task_type", "priority", "risk_level",
            "audit", "audit_title",
            "department", "department_name",
            "assigned_to", "assigned_to_detail",
            "due_date", "status", "is_overdue",
            "created_at", "updated_at",
        )


class TaskDetailSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserMiniSerializer(source="assigned_to", read_only=True)
    created_by_detail = UserMiniSerializer(source="created_by", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id", "audit", "title", "description",
            "task_type", "priority", "risk_level",
            "department", "assigned_to", "assigned_to_detail",
            "created_by", "created_by_detail",
            "template", "due_date", "status",
            "submission_data",
            "submitted_at", "reviewed_at", "is_overdue",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "submitted_at", "reviewed_at", "created_at", "updated_at",
            "created_by",
        )

    def create(self, validated):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated["created_by"] = request.user
        return super().create(validated)
