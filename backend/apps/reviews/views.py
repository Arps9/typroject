from rest_framework import viewsets

from apps.core.permissions import IsAdminOrAuditor, IsAuthenticatedAndActive

from .models import CorrectiveAction, Finding, Review
from .serializers import (
    CorrectiveActionSerializer,
    FindingSerializer,
    ReviewSerializer,
)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("task", "reviewer")
    serializer_class = ReviewSerializer
    filterset_fields = ("task", "decision")

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticatedAndActive()]
        return [IsAdminOrAuditor()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class FindingViewSet(viewsets.ModelViewSet):
    queryset = Finding.objects.select_related("audit", "task", "raised_by")
    serializer_class = FindingSerializer
    filterset_fields = ("audit", "task", "severity")

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticatedAndActive()]
        return [IsAdminOrAuditor()]

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user)


class CorrectiveActionViewSet(viewsets.ModelViewSet):
    queryset = CorrectiveAction.objects.select_related("finding", "assigned_to")
    serializer_class = CorrectiveActionSerializer
    filterset_fields = ("finding", "status", "assigned_to")
    permission_classes = [IsAuthenticatedAndActive]
