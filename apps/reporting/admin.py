from django.contrib import admin
from .models import KPI, AuditLog, StudentPerformance

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'created_at', 'updated_at']
    search_fields = ['name']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'action', 'object_repr', 'timestamp']
    list_filter = ['module', 'action', 'timestamp']
    search_fields = ['object_repr', 'user__username']

@admin.register(StudentPerformance)
class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'grade', 'attendance_percentage', 'updated_at']
    search_fields = ['student__first_name', 'student__last_name', 'course__name']
    list_filter = ['course']
