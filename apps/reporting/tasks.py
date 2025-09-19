from celery import shared_task
from django.db.models import Sum, Avg
from .models import KPI, StudentPerformance
from apps.finance.models import Payment  # Corrected import

@shared_task
def update_finance_kpis():
    # The Payment model does not have a status field. We sum all payments.
    total_collected_cents = Payment.objects.aggregate(total=Sum('amount_cents'))['total'] or 0
    total_collected = total_collected_cents / 100
    KPI.objects.update_or_create(metric='Total Fees Collected', defaults={'value': total_collected})

@shared_task
def update_student_performance_kpis():
    avg_attendance = StudentPerformance.objects.aggregate(avg_attendance=Avg('attendance_percentage'))['avg_attendance'] or 0
    KPI.objects.update_or_create(metric='Average Attendance', defaults={'value': avg_attendance})
    
    avg_score = StudentPerformance.objects.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    KPI.objects.update_or_create(metric='Average Student Score', defaults={'value': avg_score})