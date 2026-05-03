import django_filters

from .models import Audit


class AuditFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    risk_level = django_filters.CharFilter(field_name="risk_level", lookup_expr="iexact")
    audit_type = django_filters.CharFilter(field_name="audit_type", lookup_expr="iexact")
    start_after = django_filters.DateFilter(field_name="scheduled_start", lookup_expr="gte")
    start_before = django_filters.DateFilter(field_name="scheduled_start", lookup_expr="lte")
    department = django_filters.UUIDFilter(field_name="departments__id")

    class Meta:
        model = Audit
        fields = ("status", "risk_level", "audit_type", "company")
