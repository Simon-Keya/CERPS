from django.db import models
from django.conf import settings
from apps.academic.models import Student, Course
from apps.finance.models import Payment
from django.utils import timezone

class KPI(models.Model):
    """
    Key Performance Indicator model to track student or institutional metrics
    """
    metric = models.CharField(max_length=255, unique=True, default='default_metric')
    description = models.TextField(blank=True)
    value = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.metric

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
    related_object_name = models.CharField(max_length=255, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_info = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.action} on {self.object_repr} in {self.module}"

class StudentPerformance(models.Model):
    """
    Tracks student grades, attendance, or other academic KPIs
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performances')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='performances')
    grade = models.CharField(max_length=5)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    # Corrected: Removed auto_now_add=True
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.course} Performance"