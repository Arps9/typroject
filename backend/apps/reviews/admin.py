from django.contrib import admin

from .models import CorrectiveAction, Finding, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("task", "reviewer", "decision", "score", "created_at")
    list_filter = ("decision",)


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ("title", "audit", "severity", "raised_by", "created_at")
    list_filter = ("severity",)
    search_fields = ("title", "description")


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = ("title", "finding", "assigned_to", "status", "due_date")
    list_filter = ("status", "priority")
