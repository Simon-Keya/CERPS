from django.test import TestCase
from .models import Department

class DepartmentModelTest(TestCase):
    def test_create_department(self):
        dept = Department.objects.create(name="Engineering", code="ENG")
        self.assertEqual(str(dept), "Engineering")
