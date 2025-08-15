from rest_framework import serializers
from .models import KPI, AuditLog, StudentPerformance

class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = ['id', 'name', 'description', 'value', 'created_at', 'updated_at']

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'module', 'action', 'object_id', 'object_repr', 'timestamp', 'additional_info']

class StudentPerformanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = StudentPerformance
        fields = ['id', 'student', 'student_name', 'course', 'course_name', 'grade', 'attendance_percentage', 'updated_at']
