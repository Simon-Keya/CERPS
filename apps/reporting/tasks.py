from celery import shared_task
from .models import KPI, StudentPerformance
from apps.finance.models import PaymentTransaction
from django.db.models import Sum, Avg

@shared_task
def update_finance_kpis():
    total_collected = PaymentTransaction.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    KPI.objects.update_or_create(name='Total Fees Collected', defaults={'value': total_collected})

@shared_task
def update_student_performance_kpis():
    avg_attendance = StudentPerformance.objects.aggregate(avg_attendance=Avg('attendance_percentage'))['avg_attendance'] or 0
    KPI.objects.update_or_create(name='Average Attendance', defaults={'value': avg_attendance})
