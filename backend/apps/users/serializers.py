"""User serializers."""
from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.core.enums import UserRole

from .models import User


class UserMiniSerializer(serializers.ModelSerializer):
    """Lightweight user representation embedded in other resources."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "full_name", "role")


class UserSerializer(serializers.ModelSerializer):
    """Read serializer for full user details."""

    full_name = serializers.CharField(read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True, default=None)
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)

    class Meta:
        model = User
        fields = (
            "id", "email", "first_name", "last_name", "full_name", "phone",
            "role", "company", "company_name", "department", "department_name",
            "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class UserCreateSerializer(serializers.ModelSerializer):
    """Admin endpoint: create a user."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = (
            "id", "email", "first_name", "last_name", "phone",
            "role", "company", "department", "is_active", "password",
        )
        read_only_fields = ("id",)

    def validate_role(self, value: str) -> str:
        if value not in dict(UserRole.choices):
            raise serializers.ValidationError("Invalid role.")
        return value

    def create(self, validated):
        password = validated.pop("password")
        user = User.objects.create_user(password=password, **validated)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "phone",
            "role", "company", "department", "is_active",
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
