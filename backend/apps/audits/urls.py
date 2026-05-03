from rest_framework.routers import DefaultRouter

from .views import AuditViewSet

router = DefaultRouter()
router.register("", AuditViewSet, basename="audits")

urlpatterns = router.urls
