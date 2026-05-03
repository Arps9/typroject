from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "industry", "contact_email", "created_at")
    search_fields = ("name", "code", "industry")
    list_filter = ("industry",)
