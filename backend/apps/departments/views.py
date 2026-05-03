from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.core.permissions import IsAdmin, IsAuthenticatedAndActive

from .models import Department
from .serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = (
        Department.objects.select_related("company", "manager")
        .annotate(user_count=Count("users", distinct=True))
    )
    serializer_class = DepartmentSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("company",)
    search_fields = ("name", "code")
    ordering_fields = ("name", "created_at")
    ordering = ("name",)

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticatedAndActive()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.is_authenticated and not u.is_admin and u.company_id:
            qs = qs.filter(company_id=u.company_id)
        return qs
