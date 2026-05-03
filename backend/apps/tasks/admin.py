from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "audit", "department", "assigned_to",
                    "status", "due_date", "priority", "risk_level")
    list_filter = ("status", "task_type", "priority", "risk_level", "department")
    search_fields = ("title", "description")
    autocomplete_fields = ("audit", "department", "assigned_to", "created_by")
