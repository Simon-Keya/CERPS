import logging
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Program, Instructor, Course, Student, Subject, Timetable, Grade, TeachingAssignment, AcademicYear
from apps.admissions.models import Intake, Application, ApplicationDocument, ApplicationReview, Offer, AdmissionDecision
from .serializers import (
    ProgramSerializer, InstructorSerializer, CourseSerializer, StudentSerializer,
    SubjectSerializer, TimetableSerializer, GradeSerializer, TeachingAssignmentSerializer, AcademicYearSerializer
)

logger = logging.getLogger(__name__)

# New ViewSet for AcademicYear
class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_current"]
    search_fields = ["name"]
    ordering = ["-start_date"]

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related("department", "college").all()
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department", "college"]
    search_fields = ["name"]
    ordering = ["-created_at"]

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.select_related("user", "department").all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department"]
    search_fields = ["user__login_id", "user__first_name", "user__last_name"]
    ordering = ["-created_at"]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("program").all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["program"]
    search_fields = ["name"]
    ordering = ["-created_at"]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related("user", "program", "department").all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["program", "department"]
    search_fields = ["user__login_id", "admission_number"]
    ordering = ["-created_at"]

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related("course").all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["course"]
    search_fields = ["name"]
    ordering = ["-created_at"]

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.select_related("course").all()
    serializer_class = TimetableSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["course", "day"]
    search_fields = ["course__name"]
    ordering = ["-created_at"]

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.select_related("student", "subject").all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "subject"]
    search_fields = ["student__admission_number", "subject__name"]
    ordering = ["-created_at"]

class TeachingAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TeachingAssignment.objects.select_related("instructor", "course").all()
    serializer_class = TeachingAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["instructor", "course"]
    search_fields = ["instructor__user__login_id", "course__name"]
    ordering = ["-created_at"]