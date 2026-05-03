"""JWT authentication endpoints."""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.responses import envelope
from apps.users.serializers import UserSerializer

from .serializers import LoginSerializer, LogoutSerializer


class LoginView(TokenObtainPairView):
    """POST /api/v1/auth/login/  -> {access, refresh, user}"""

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            return envelope(
                None,
                message="Invalid credentials",
                status=status.HTTP_401_UNAUTHORIZED,
                errors=[{"detail": str(exc)}],
            )

        data = serializer.validated_data

        # Capture client IP on the user model for audit purposes
        user = serializer.user
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")
        if ip:
            user.last_login_ip = ip
            user.save(update_fields=["last_login_ip"])

        return envelope(data, message="Login successful")


class RefreshView(TokenRefreshView):
    """POST /api/v1/auth/refresh/  -> {access, refresh}"""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except TokenError as exc:
            return envelope(
                None,
                message="Invalid refresh token",
                status=status.HTTP_401_UNAUTHORIZED,
                errors=[{"detail": str(exc)}],
            )
        return envelope(response.data, message="Token refreshed")


class LogoutView(APIView):
    """POST /api/v1/auth/logout/  -> blacklist refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = LogoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            token = RefreshToken(ser.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            pass  # idempotent
        return envelope(None, message="Logged out", status=status.HTTP_200_OK)


class MeView(APIView):
    """GET /api/v1/auth/me/  -> current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return envelope(UserSerializer(request.user).data, message="Current user")
