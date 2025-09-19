from rest_framework import serializers
from .models import KPI, AuditLog, StudentPerformance
from apps.academic.models import Student, Course

class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = ['id', 'metric', 'value', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'module', 'action', 'object_repr', 'object_id', 'timestamp', 'additional_info']
        read_only_fields = ['id', 'timestamp', 'user']

class StudentPerformanceSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = StudentPerformance
        fields = ['id', 'student', 'course', 'grade', 'attendance_percentage', 'score', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']