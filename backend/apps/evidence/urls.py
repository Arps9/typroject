from rest_framework.routers import DefaultRouter

from .views import EvidenceFileViewSet

router = DefaultRouter()
router.register("", EvidenceFileViewSet, basename="evidence")

urlpatterns = router.urls
