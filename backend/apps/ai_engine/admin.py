from django.contrib import admin

from .models import AIExtractionResult


@admin.register(AIExtractionResult)
class AIExtractionResultAdmin(admin.ModelAdmin):
    list_display = ("evidence", "result", "confidence", "created_at")
    list_filter = ("result",)
