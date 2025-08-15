from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import KPI, AuditLog, StudentPerformance
from .serializers import KPISerializer, AuditLogSerializer, StudentPerformanceSerializer
from django.db.models import Avg, Count

class KPIViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [permissions.IsAdminUser]

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False)
    def recent_actions(self, request):
        logs = self.queryset.order_by('-timestamp')[:50]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

class StudentPerformanceViewSet(viewsets.ModelViewSet):
    queryset = StudentPerformance.objects.all()
    serializer_class = StudentPerformanceSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def course_average(self, request):
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response({'error': 'course_id is required'}, status=400)
        avg_grade = self.queryset.filter(course_id=course_id).aggregate(average=Avg('attendance_percentage'))
        return Response({'course_id': course_id, 'average_attendance': avg_grade['average']})
