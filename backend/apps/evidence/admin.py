from django.contrib import admin

from .models import EvidenceFile


@admin.register(EvidenceFile)
class EvidenceFileAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "task", "uploaded_by", "size_bytes", "created_at")
    search_fields = ("original_filename",)
