"""Authentication serializers.

Wraps SimpleJWT to attach the authenticated user payload to every login
response so the frontend doesn't need a follow-up /me call.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.serializers import UserSerializer

User = get_user_model()


class LoginSerializer(TokenObtainPairSerializer):
    """Username field is the email; returns user payload alongside tokens."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
