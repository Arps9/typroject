from rest_framework.routers import DefaultRouter

from .views import CorrectiveActionViewSet, FindingViewSet, ReviewViewSet

router = DefaultRouter()
router.register("reviews", ReviewViewSet, basename="reviews")
router.register("findings", FindingViewSet, basename="findings")
router.register("corrective-actions", CorrectiveActionViewSet, basename="corrective-actions")

urlpatterns = router.urls
