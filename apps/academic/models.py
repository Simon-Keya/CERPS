from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import College, Department


class Program(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    credits = models.PositiveIntegerField(default=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    subject_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.full_name or str(self.user)


class TeachingAssignment(models.Model):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=9)

    class Meta:
        unique_together = ('instructor', 'subject', 'semester', 'academic_year')

    def __str__(self):
        return f"{self.instructor} -> {self.subject}"


class Timetable(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)


class Grade(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=9)

    class Meta:
        unique_together = ('student', 'subject', 'semester', 'academic_year')


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    admission_number = models.CharField(max_length=20, unique=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="students")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    programs = models.ManyToManyField(Program, blank=True, related_name="enrolled_students")
    enrollment_date = models.DateField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} ({self.admission_number})"
