"""Root URL configuration for the Compliance Audit project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


api_v1_patterns = [
    path("auth/", include("apps.authentication.urls")),
    path("companies/", include("apps.companies.urls")),
    path("departments/", include("apps.departments.urls")),
    path("users/", include("apps.users.urls")),
    path("audits/", include("apps.audits.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("templates/", include("apps.templates_engine.urls")),
    path("evidence/", include("apps.evidence.urls")),
    path("ai/", include("apps.ai_engine.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("reports/", include("apps.reports.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("analytics/", include("apps.analytics.urls")),
]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "api"), namespace="v1")),
    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
