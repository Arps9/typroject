from rest_framework import serializers

from .models import AuditLog, Notification


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id", "title", "body", "channel", "link",
            "read_at", "is_read", "created_at",
        )
        read_only_fields = ("read_at", "is_read", "created_at")

    def get_is_read(self, obj) -> bool:
        return obj.read_at is not None


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = (
            "id", "user", "user_email", "action", "path",
            "status_code", "metadata", "created_at",
        )
