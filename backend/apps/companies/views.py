from django.db.models import Count
from rest_framework import filters, viewsets

from apps.core.permissions import IsAdmin, IsAuthenticatedAndActive

from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """CRUD for companies.  Read open to all authenticated users; writes admin only."""

    queryset = (
        Company.objects.annotate(
            department_count=Count("departments", distinct=True),
            user_count=Count("users", distinct=True),
        )
    )
    serializer_class = CompanySerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "code", "industry")
    ordering_fields = ("name", "created_at")
    ordering = ("name",)

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticatedAndActive()]
        return [IsAdmin()]
