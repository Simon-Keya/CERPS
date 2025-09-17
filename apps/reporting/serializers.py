from rest_framework import serializers
from .models import KPI, AuditLog, StudentPerformance
from apps.admissions.models import AcademicYear
from apps.users.models import User
from apps.academic.models import Student, Course

class KPISerializer(serializers.ModelSerializer):
    academic_year = serializers.StringRelatedField()

    class Meta:
        model = KPI
        fields = ['id', 'metric', 'value', 'academic_year', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'timestamp', 'details']
        read_only_fields = ['id', 'timestamp']

class StudentPerformanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    course = serializers.StringRelatedField()

    class Meta:
        model = StudentPerformance
        fields = ['id', 'student', 'course', 'score', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']