from django.test import TestCase
from .models import Course, Department

class CourseModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering", code="ENG")
        Course.objects.create(title="Intro to CS", code="CS101", department=self.department, credits=3)

    def test_course_created(self):
        course = Course.objects.get(code="CS101")
        self.assertEqual(course.title, "Intro to CS")
