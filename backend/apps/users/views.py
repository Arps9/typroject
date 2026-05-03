"""User management views (admin-only for create/update/delete)."""
from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsAdmin, IsAuthenticatedAndActive
from apps.core.responses import envelope

from .models import User
from .serializers import (
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD for users.  All write actions require admin role."""

    queryset = User.objects.select_related("company", "department").all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("email", "first_name", "last_name")
    ordering_fields = ("email", "created_at")
    ordering = ("email",)

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in {"update", "partial_update"}:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve", "me", "change_password"}:
            return [IsAuthenticatedAndActive()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        # Non-admins can only see users in their own company
        if u.is_authenticated and not u.is_admin and u.company_id:
            qs = qs.filter(company_id=u.company_id)
        return qs

    # --- Custom actions ----------------------------------------------------
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        return envelope(UserSerializer(request.user).data, message="Current user")

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        ser = ChangePasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        if not request.user.check_password(ser.validated_data["old_password"]):
            return envelope(
                None, message="Current password is incorrect",
                status=status.HTTP_400_BAD_REQUEST,
                errors=[{"old_password": "Incorrect"}],
            )
        request.user.set_password(ser.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return envelope(None, message="Password updated")
