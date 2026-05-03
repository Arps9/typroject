from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    department_count = serializers.IntegerField(read_only=True)
    user_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = (
            "id", "name", "code", "industry", "address",
            "contact_email", "logo_url",
            "department_count", "user_count",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
