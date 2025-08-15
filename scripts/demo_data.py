import os
import django
from faker import Faker
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cerps.settings")
django.setup()

from apps.users.models import CustomUser
from apps.academic.models import Course, Subject

fake = Faker()

def seed_students(n=10):
    for _ in range(n):
        student = CustomUser.objects.create_user(
            username=fake.user_name(),
            password="student123",
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_student=True
        )
        print(f"Created student: {student.username}")

def seed_courses(n=5):
    for _ in range(n):
        course = Course.objects.create(
            name=fake.word().capitalize() + " Studies",
            code=fake.bothify(text="???###")
        )
        print(f"Created course: {course.name}")

if __name__ == "__main__":
    seed_courses()
    seed_students()
