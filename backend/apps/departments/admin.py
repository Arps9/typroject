from django.contrib import admin

from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "manager", "created_at")
    list_filter = ("company",)
    search_fields = ("name", "code", "description")
