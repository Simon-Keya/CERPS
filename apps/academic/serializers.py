from rest_framework import serializers
from .models import Program, Instructor, Course, Student, Subject, Timetable, Grade, TeachingAssignment, AcademicYear
from apps.hr.models import Department
from apps.core.models import College
from apps.users.models import User

# Serializer for AcademicYear
class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for Program
class ProgramSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    college = serializers.PrimaryKeyRelatedField(queryset=College.objects.all())

    class Meta:
        model = Program
        fields = ['id', 'name', 'department', 'college', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for Instructor
class InstructorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Instructor
        fields = ['id', 'user', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for Course
class CourseSerializer(serializers.ModelSerializer):
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Course
        fields = ['id', 'name', 'program', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for Student
class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), allow_null=True, required=False)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Student
        fields = ['id', 'user', 'admission_number', 'program', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for Subject
class SubjectSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'course', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for Timetable
class TimetableSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Timetable
        fields = ['id', 'course', 'day', 'start_time', 'end_time', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for Grade
class GradeSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True, required=False)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Grade
        fields = ['id', 'student', 'subject', 'score', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for TeachingAssignment
class TeachingAssignmentSerializer(serializers.ModelSerializer):
    instructor = serializers.PrimaryKeyRelatedField(queryset=Instructor.objects.all(), allow_null=True, required=False)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), allow_null=True, required=False)

    class Meta:
        model = TeachingAssignment
        fields = ['id', 'instructor', 'course', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']