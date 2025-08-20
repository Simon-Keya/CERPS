from rest_framework.routers import DefaultRouter
from .views import CollegeViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r'college', CollegeViewSet)
router.register(r'departments', DepartmentViewSet)

urlpatterns = router.urls
