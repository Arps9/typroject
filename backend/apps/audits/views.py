from __future__ import annotations

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from apps.core.permissions import IsAdminOrAuditor, IsAuthenticatedAndActive
from apps.core.responses import envelope

from .filters import AuditFilter
from .models import Audit
from .serializers import AuditDetailSerializer, AuditListSerializer
from .services import AuditTransitionError, transition_audit


class AuditViewSet(viewsets.ModelViewSet):
    queryset = (
        Audit.objects.select_related("company", "lead_auditor")
        .prefetch_related("departments", "auditors")
    )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = AuditFilter
    search_fields = ("title", "description")
    ordering_fields = ("scheduled_start", "created_at", "status")
    ordering = ("-scheduled_start",)

    def get_serializer_class(self):
        if self.action == "list":
            return AuditListSerializer
        return AuditDetailSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticatedAndActive()]
        return [IsAdminOrAuditor()]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if not u.is_authenticated:
            return qs.none()

        # Admin sees everything in their company
        if u.is_admin and u.company_id:
            return qs.filter(company_id=u.company_id)

        # Auditor sees audits they lead/participate in
        if u.is_auditor:
            return qs.filter(Q(lead_auditor=u) | Q(auditors=u)).distinct()

        # Department user sees audits scoped to their department
        if u.is_department_user and u.department_id:
            return qs.filter(departments__id=u.department_id).distinct()

        return qs.none()

    # --- transitions ------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        audit = self.get_object()
        target = request.data.get("status")
        if not target:
            return envelope(
                None, message="'status' is required",
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            transition_audit(audit, target)
        except AuditTransitionError as exc:
            return envelope(
                None, message=str(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return envelope(AuditDetailSerializer(audit).data, message="Audit updated")
