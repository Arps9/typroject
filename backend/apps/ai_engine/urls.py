from rest_framework.routers import DefaultRouter

from .views import AIExtractionResultViewSet

router = DefaultRouter()
router.register("results", AIExtractionResultViewSet, basename="ai-results")

urlpatterns = router.urls
