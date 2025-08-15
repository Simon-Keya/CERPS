from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='headed_departments'
    )

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    credits = models.IntegerField()

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
        return f"{self.user.get_full_name()}"

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
    day_of_week = models.CharField(max_length=10)  # e.g., Monday
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
