from rest_framework import filters, viewsets

from apps.core.permissions import IsAdminOrAuditor, IsAuthenticatedAndActive

from .models import TaskTemplate
from .serializers import TaskTemplateSerializer


class TaskTemplateViewSet(viewsets.ModelViewSet):
    queryset = TaskTemplate.objects.all()
    serializer_class = TaskTemplateSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering = ("name",)

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticatedAndActive()]
        return [IsAdminOrAuditor()]
