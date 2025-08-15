from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, AcademicYearViewSet, ProgramViewSet,
    GradingScaleViewSet, CollegeConfigViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'grading-scales', GradingScaleViewSet)
router.register(r'college-config', CollegeConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
