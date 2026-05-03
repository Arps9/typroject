import django_filters

from .models import Task


class TaskFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    task_type = django_filters.CharFilter(field_name="task_type", lookup_expr="iexact")
    priority = django_filters.CharFilter(field_name="priority", lookup_expr="iexact")
    risk_level = django_filters.CharFilter(field_name="risk_level", lookup_expr="iexact")
    audit = django_filters.UUIDFilter(field_name="audit__id")
    department = django_filters.UUIDFilter(field_name="department__id")
    assigned_to = django_filters.UUIDFilter(field_name="assigned_to__id")
    due_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")

    class Meta:
        model = Task
        fields = ("status", "task_type", "priority", "risk_level",
                  "audit", "department", "assigned_to")
