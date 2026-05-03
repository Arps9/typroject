from rest_framework.routers import DefaultRouter

from .views import TaskTemplateViewSet

router = DefaultRouter()
router.register("", TaskTemplateViewSet, basename="templates")

urlpatterns = router.urls
