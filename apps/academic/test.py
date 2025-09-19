import factory
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from apps.users.models import User
from apps.hr.models import Department
from apps.core.models import College
from apps.academic.models import AcademicYear, Program, Instructor, Course, Student, Subject, Timetable, Grade, TeachingAssignment
from datetime import date # Import the date class

# Factory Definitions for Academic Models
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    login_id = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.Sequence(lambda n: f'testuser{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True

class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department
    name = factory.Sequence(lambda n: f'Department {n}')

class CollegeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = College
    name = factory.Sequence(lambda n: f'College {n}')

class AcademicYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AcademicYear
    name = factory.Sequence(lambda n: f'202{n}/202{n+1}')
    start_date = factory.LazyFunction(timezone.now().date)
    end_date = factory.LazyFunction(lambda: timezone.now().date() + timezone.timedelta(days=365))

class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program
    name = factory.Sequence(lambda n: f'Program {n}')
    department = factory.SubFactory(DepartmentFactory)
    college = factory.SubFactory(CollegeFactory)

class InstructorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Instructor
    user = factory.SubFactory(UserFactory)
    department = factory.SubFactory(DepartmentFactory)

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
    name = factory.Sequence(lambda n: f'Course {n}')
    program = factory.SubFactory(ProgramFactory)

class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student
    user = factory.SubFactory(UserFactory)
    admission_number = factory.Sequence(lambda n: f'ADM-{n:04d}')
    program = factory.SubFactory(ProgramFactory)
    department = factory.SubFactory(DepartmentFactory)

class SubjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subject
    name = factory.Sequence(lambda n: f'Subject {n}')
    course = factory.SubFactory(CourseFactory)

class TimetableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Timetable
    course = factory.SubFactory(CourseFactory)
    day = 'Monday'
    start_time = timezone.now().time()
    end_time = factory.LazyFunction(lambda: (timezone.now() + timezone.timedelta(hours=2)).time())

class GradeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Grade
    student = factory.SubFactory(StudentFactory)
    subject = factory.SubFactory(SubjectFactory)
    score = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True, min_value=0, max_value=100)

class TeachingAssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeachingAssignment
    instructor = factory.SubFactory(InstructorFactory)
    course = factory.SubFactory(CourseFactory)


# API Tests for Academic App
class AcademicAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Authenticate with a staff user to pass permission checks
        self.staff_user = UserFactory(is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=self.staff_user)

        # Pre-create related objects for tests
        self.academic_year = AcademicYearFactory()
        self.department = DepartmentFactory()
        self.college = CollegeFactory()
        self.program = ProgramFactory(department=self.department, college=self.college)
        self.instructor = InstructorFactory(department=self.department)
        self.course = CourseFactory(program=self.program)
        self.student = StudentFactory(program=self.program, department=self.department)
        self.subject = SubjectFactory(course=self.course)

    def test_create_academic_year(self):
        url = reverse('academicyear-list')
        data = {
            'name': '2025/2026', 
            'start_date': date(2025, 9, 1), 
            'end_date': date(2026, 8, 31)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(AcademicYear.objects.count(), 2)

    def test_create_program(self):
        url = reverse('program-list')
        data = {'name': 'New Program', 'department': self.department.id, 'college': self.college.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Program.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Program')

    def test_create_instructor(self):
        url = reverse('instructor-list')
        user = UserFactory.create()
        data = {'user': user.id, 'department': self.department.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Instructor.objects.count(), 2)

    def test_create_course(self):
        url = reverse('course-list')
        data = {'name': 'New Course', 'program': self.program.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_create_student(self):
        url = reverse('student-list')
        user = UserFactory.create()
        data = {
            'user': user.id,
            'admission_number': 'ADM-9999',
            'program': self.program.id,
            'department': self.department.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Student.objects.count(), 2)

    def test_create_subject(self):
        url = reverse('subject-list')
        data = {'name': 'New Subject', 'course': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subject.objects.count(), 2)

    def test_create_timetable(self):
        url = reverse('timetable-list')
        data = {'course': self.course.id, 'day': 'Friday', 'start_time': '09:00:00', 'end_time': '11:00:00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Timetable.objects.count(), 1)

    def test_create_grade(self):
        url = reverse('grade-list')
        data = {'student': self.student.id, 'subject': self.subject.id, 'score': 95.5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 1)

    def test_create_teaching_assignment(self):
        url = reverse('teachingassignment-list')
        data = {'instructor': self.instructor.id, 'course': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TeachingAssignment.objects.count(), 1)