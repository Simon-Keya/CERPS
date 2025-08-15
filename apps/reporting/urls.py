from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import KPIViewSet, AuditLogViewSet, StudentPerformanceViewSet

router = DefaultRouter()
router.register(r'kpi', KPIViewSet, basename='kpi')
router.register(r'audit', AuditLogViewSet, basename='audit')
router.register(r'student-performance', StudentPerformanceViewSet, basename='student-performance')

urlpatterns = [
    path('', include(router.urls)),
]
