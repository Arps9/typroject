from rest_framework import serializers

from apps.users.serializers import UserMiniSerializer

from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    manager_detail = UserMiniSerializer(source="manager", read_only=True)
    user_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = (
            "id", "company", "company_name", "name", "code", "description",
            "manager", "manager_detail", "user_count",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
