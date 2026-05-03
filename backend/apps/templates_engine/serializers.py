from rest_framework import serializers

from .models import TaskTemplate


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = (
            "id", "company", "name", "description", "version", "is_active",
            "schema", "validation_rules",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate_schema(self, value):
        if not isinstance(value, dict) or "fields" not in value:
            raise serializers.ValidationError(
                "schema must be an object with a 'fields' array"
            )
        if not isinstance(value["fields"], list):
            raise serializers.ValidationError("schema.fields must be a list")
        # TODO(phase-7): full per-field validation
        return value
