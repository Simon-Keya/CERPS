import logging
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import KPI, AuditLog, StudentPerformance
from apps.admissions.models import AcademicYear, Intake, Application, ApplicationDocument, ApplicationReview, Offer, AdmissionDecision
from .serializers import KPISerializer, AuditLogSerializer, StudentPerformanceSerializer

logger = logging.getLogger(__name__)

class KPIViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["metric", "academic_year"]
    search_fields = ["metric"]
    ordering = ["-created_at"]

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["action", "user"]
    search_fields = ["action", "user__login_id"]
    ordering = ["-timestamp"]

class StudentPerformanceViewSet(viewsets.ModelViewSet):
    queryset = StudentPerformance.objects.all()
    serializer_class = StudentPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "course"]
    search_fields = ["student__student_id", "course__name"]
    ordering = ["-created_at"]