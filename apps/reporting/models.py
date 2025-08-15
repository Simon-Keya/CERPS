from django.db import models
from django.conf import settings
from apps.core.models import Student, Course
from apps.finance.models import PaymentTransaction

class KPI(models.Model):
    """
    Key Performance Indicator model to track student or institutional metrics
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    value = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AuditLog(models.Model):
    """
    Tracks changes across critical modules for compliance & reporting
    """
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    module = models.CharField(max_length=50)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_info = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

class StudentPerformance(models.Model):
    """
    Tracks student grades, attendance, or other academic KPIs
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=5)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
