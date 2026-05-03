from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, NotificationViewSet

# Two routers to avoid the empty-prefix collision with the audit-log path.
notifications_router = DefaultRouter()
notifications_router.register("", NotificationViewSet, basename="notifications")

audit_log_router = DefaultRouter()
audit_log_router.register("audit-log", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    # /api/v1/notifications/audit-log/  -> audit log
    path("", include(audit_log_router.urls)),
    # /api/v1/notifications/  -> notifications
    path("", include(notifications_router.urls)),
]
