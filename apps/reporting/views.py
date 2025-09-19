import logging
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import KPI, AuditLog, StudentPerformance
from .serializers import KPISerializer, AuditLogSerializer, StudentPerformanceSerializer
from .permissions import IsStaffOrReadOnly

logger = logging.getLogger(__name__)

class KPIViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["metric"]
    search_fields = ["metric", "description"]
    ordering_fields = ["created_at", "value"]
    ordering = ["-created_at"]

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["action", "user", "module"]
    search_fields = ["object_repr", "user__login_id"]
    ordering_fields = ["timestamp", "module"]
    ordering = ["-timestamp"]

class StudentPerformanceViewSet(viewsets.ModelViewSet):
    queryset = StudentPerformance.objects.all()
    serializer_class = StudentPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "course"]
    search_fields = ["student__user__login_id", "course__name"]
    ordering_fields = ["updated_at", "score", "attendance_percentage"]
    ordering = ["-updated_at"]