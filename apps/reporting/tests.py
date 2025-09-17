from django.test import TestCase
from apps.academic.models import Student, Course
from .models import KPI, StudentPerformance, AuditLog

class ReportingTestCase(TestCase):
    def setUp(self):
        self.student = Student.objects.create(admission_number="ADM100", first_name="Alice", last_name="Smith")
        self.course = Course.objects.create(name="Mathematics", code="MATH101")

    def test_kpi_creation(self):
        kpi = KPI.objects.create(name="Test KPI", value=42)
        self.assertEqual(kpi.value, 42)

    def test_student_performance_creation(self):
        perf = StudentPerformance.objects.create(student=self.student, course=self.course, grade="A", attendance_percentage=95)
        self.assertEqual(perf.grade, "A")
