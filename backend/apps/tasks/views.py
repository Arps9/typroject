from __future__ import annotations

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from apps.core.permissions import IsAdminOrAuditor, IsAuthenticatedAndActive
from apps.core.responses import envelope

from .filters import TaskFilter
from .models import Task
from .serializers import TaskDetailSerializer, TaskListSerializer
from .services import TaskTransitionError, assign_task, transition_task


class TaskViewSet(viewsets.ModelViewSet):
    queryset = (
        Task.objects.select_related(
            "audit", "department", "assigned_to", "created_by", "template"
        )
    )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = TaskFilter
    search_fields = ("title", "description")
    ordering_fields = ("due_date", "created_at", "status", "priority")
    ordering = ("due_date",)

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        return TaskDetailSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy",
                           "transition", "assign"}:
            return [IsAdminOrAuditor()]
        return [IsAuthenticatedAndActive()]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if not u.is_authenticated:
            return qs.none()

        if u.is_admin and u.company_id:
            return qs.filter(audit__company_id=u.company_id)

        if u.is_auditor:
            return qs.filter(
                Q(audit__lead_auditor=u) | Q(audit__auditors=u) | Q(created_by=u)
            ).distinct()

        if u.is_department_user:
            return qs.filter(
                Q(assigned_to=u) | Q(department_id=u.department_id)
            ).distinct()

        return qs.none()

    # --- transitions ---
    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        task = self.get_object()
        target = request.data.get("status")
        if not target:
            return envelope(None, message="'status' is required",
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            transition_task(task, target, by=request.user)
        except TaskTransitionError as exc:
            return envelope(None, message=str(exc),
                            status=status.HTTP_400_BAD_REQUEST)
        return envelope(TaskDetailSerializer(task).data, message="Task updated")

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        from apps.users.models import User
        task = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return envelope(None, message="'user_id' is required",
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return envelope(None, message="User not found",
                            status=status.HTTP_404_NOT_FOUND)
        assign_task(task, target_user)
        return envelope(TaskDetailSerializer(task).data, message="Task assigned")

    @action(detail=False, methods=["get"], url_path="my")
    def my(self, request):
        """Convenience endpoint for the current user's tasks."""
        qs = self.get_queryset().filter(assigned_to=request.user)
        page = self.paginate_queryset(qs)
        ser = TaskListSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return envelope(ser.data, message="My tasks")
