import factory
import logging
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.db import models
from apps.users.models import User
from apps.academic.models import Student, Course
from apps.finance.models import Payment, Ledger, Invoice
from .models import KPI, AuditLog, StudentPerformance
from .tasks import update_finance_kpis, update_student_performance_kpis

# Silence Celery logging during tests
logging.getLogger('celery').setLevel(logging.CRITICAL)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    login_id = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student
    
    user = factory.SubFactory(UserFactory)
    student_id = factory.Sequence(lambda n: f'ADM-{n:04d}') 

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    name = factory.Sequence(lambda n: f'Course {n}')

class LedgerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ledger
    
    student = factory.SubFactory(StudentFactory)
    balance_cents = 0

class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice
    
    ledger = factory.SubFactory(LedgerFactory)
    amount_cents = factory.Faker('pyint', min_value=1000, max_value=50000)
    due_date = timezone.now().date() + timezone.timedelta(days=30)
    status = 'pending'

class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment
    
    invoice = factory.SubFactory(InvoiceFactory)
    amount_cents = factory.Faker('pyint', min_value=1000, max_value=50000)
    payment_method = 'bank_transfer'

class KPIFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KPI
    
    metric = factory.Sequence(lambda n: f'KPI Metric {n}')
    value = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True)

class AuditLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditLog

    user = factory.SubFactory(UserFactory)
    module = 'TestModule'
    action = 'create'
    object_repr = 'Test Object'

class StudentPerformanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentPerformance

    student = factory.SubFactory(StudentFactory)
    course = factory.SubFactory(CourseFactory)
    grade = 'A'
    attendance_percentage = 95.5
    score = 88.0

class ReportingModelTests(TestCase):
    def test_kpi_creation(self):
        kpi = KPIFactory()
        self.assertIsInstance(kpi, KPI)
        self.assertIsNotNone(kpi.created_at)

    def test_audit_log_creation(self):
        log = AuditLogFactory()
        self.assertIsInstance(log, AuditLog)
        self.assertEqual(log.action, 'create')

    def test_student_performance_creation(self):
        performance = StudentPerformanceFactory()
        self.assertIsInstance(performance, StudentPerformance)
        self.assertIsNotNone(performance.updated_at)
        self.assertEqual(performance.grade, 'A')

class ReportingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = UserFactory(is_staff=True, is_superuser=True)
        self.regular_user = UserFactory()
        self.client.force_authenticate(user=self.staff_user)

        self.kpi = KPIFactory()
        self.audit_log = AuditLogFactory()
        self.student = StudentFactory()
        self.course = CourseFactory()

    def test_list_kpis_as_staff(self):
        url = reverse('kpi-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_kpi_as_staff(self):
        url = reverse('kpi-list')
        data = {'metric': 'New Metric', 'value': 123.45}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KPI.objects.count(), 2)

    def test_create_kpi_as_regular_user_denied(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('kpi-list')
        data = {'metric': 'New Metric', 'value': 123.45}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_audit_logs_as_admin(self):
        url = reverse('auditlog-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_audit_logs_as_regular_user_denied(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('auditlog-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_student_performances_as_staff(self):
        url = reverse('studentperformance-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_student_performance_as_staff(self):
        url = reverse('studentperformance-list')
        student = StudentFactory()
        course = CourseFactory()
        data = {
            'student': student.id,
            'course': course.id,
            'grade': 'B',
            'attendance_percentage': 85.0,
            'score': 75.5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentPerformance.objects.count(), 1)
    
    def test_search_kpis(self):
        KPI.objects.create(metric="Total Fees", value=100)
        url = reverse('kpi-list') + '?search=Total Fees'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['metric'], 'Total Fees')

class ReportingTaskTests(TestCase):
    def setUp(self):
        self.student1 = StudentFactory()
        self.course1 = CourseFactory()
        self.student2 = StudentFactory()
        self.course2 = CourseFactory()

    def test_update_finance_kpis_task(self):
        invoice = InvoiceFactory()
        Payment.objects.create(invoice=invoice, amount_cents=10000)
        Payment.objects.create(invoice=invoice, amount_cents=20000)
        
        total_paid_cents = Payment.objects.aggregate(total=models.Sum('amount_cents'))['total'] or 0
        KPI.objects.update_or_create(metric='Total Fees Collected', defaults={'value': total_paid_cents / 100})

        kpi = KPI.objects.get(metric='Total Fees Collected')
        self.assertEqual(kpi.value, 300.0)

    def test_update_student_performance_kpis_task(self):
        StudentPerformance.objects.create(
            student=self.student1,
            course=self.course1,
            grade='A',
            attendance_percentage=90.0,
            score=92.0
        )
        StudentPerformance.objects.create(
            student=self.student2,
            course=self.course2,
            grade='B',
            attendance_percentage=80.0,
            score=85.0
        )

        update_student_performance_kpis()
        avg_attendance_kpi = KPI.objects.get(metric='Average Attendance')
        self.assertAlmostEqual(avg_attendance_kpi.value, 85.0)

        avg_score_kpi = KPI.objects.get(metric='Average Student Score')
        self.assertAlmostEqual(avg_score_kpi.value, 88.5)