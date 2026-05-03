from django.contrib import admin

from .models import AuditLog, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "channel", "read_at", "created_at")
    list_filter = ("channel",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "path", "status_code", "created_at")
    list_filter = ("action", "status_code")
    search_fields = ("path",)
    readonly_fields = ("user", "action", "path", "status_code", "metadata", "created_at")
