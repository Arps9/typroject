from django.contrib import admin

from .models import Audit


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "status", "audit_type",
                    "scheduled_start", "scheduled_end", "lead_auditor")
    list_filter = ("status", "audit_type", "risk_level", "company")
    search_fields = ("title", "description")
    autocomplete_fields = ("lead_auditor",)
    filter_horizontal = ("departments", "auditors")
