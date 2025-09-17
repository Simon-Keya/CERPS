from rest_framework import serializers
from .models import Program, Instructor, Course, Student, Subject, Timetable, Grade, TeachingAssignment
from apps.hr.models import Department
from apps.core.models import College
from apps.users.models import User

class ProgramSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    college = serializers.StringRelatedField()

    class Meta:
        model = Program
        fields = ['id', 'name', 'department', 'college', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class InstructorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    department = serializers.StringRelatedField()

    class Meta:
        model = Instructor
        fields = ['id', 'user', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CourseSerializer(serializers.ModelSerializer):
    program = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'program', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    program = serializers.StringRelatedField()
    department = serializers.StringRelatedField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'student_id', 'program', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SubjectSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'course', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TimetableSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField()

    class Meta:
        model = Timetable
        fields = ['id', 'course', 'day', 'start_time', 'end_time', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class GradeSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    subject = serializers.StringRelatedField()

    class Meta:
        model = Grade
        fields = ['id', 'student', 'subject', 'score', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TeachingAssignmentSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField()
    course = serializers.StringRelatedField()

    class Meta:
        model = TeachingAssignment
        fields = ['id', 'instructor', 'course', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']