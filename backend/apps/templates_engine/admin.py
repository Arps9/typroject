from django.contrib import admin

from .models import TaskTemplate


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "company", "is_active", "created_at")
    list_filter = ("is_active", "company")
    search_fields = ("name", "description")
