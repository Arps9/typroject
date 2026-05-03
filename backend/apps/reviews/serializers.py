from rest_framework import serializers

from apps.users.serializers import UserMiniSerializer

from .models import CorrectiveAction, Finding, Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_detail = UserMiniSerializer(source="reviewer", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id", "task", "reviewer", "reviewer_detail",
            "decision", "score", "comments", "created_at",
        )
        read_only_fields = ("created_at", "reviewer")


class FindingSerializer(serializers.ModelSerializer):
    raised_by_detail = UserMiniSerializer(source="raised_by", read_only=True)

    class Meta:
        model = Finding
        fields = (
            "id", "audit", "task", "raised_by", "raised_by_detail",
            "title", "description", "severity",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "raised_by")


class CorrectiveActionSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserMiniSerializer(source="assigned_to", read_only=True)

    class Meta:
        model = CorrectiveAction
        fields = (
            "id", "finding", "assigned_to", "assigned_to_detail",
            "title", "description", "priority", "due_date",
            "status", "resolution_notes",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
