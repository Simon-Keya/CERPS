from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KPIViewSet, AuditLogViewSet, StudentPerformanceViewSet

router = DefaultRouter()
router.register(r'kpis', KPIViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'student-performances', StudentPerformanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]