from rest_framework import viewsets, permissions
from .models import Department, AcademicYear, Program, GradingScale, CollegeConfig
from .serializers import (
    DepartmentSerializer, AcademicYearSerializer, ProgramSerializer,
    GradingScaleSerializer, CollegeConfigSerializer
)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

class GradingScaleViewSet(viewsets.ModelViewSet):
    queryset = GradingScale.objects.all()
    serializer_class = GradingScaleSerializer
    permission_classes = [permissions.IsAuthenticated]

class CollegeConfigViewSet(viewsets.ModelViewSet):
    queryset = CollegeConfig.objects.all()
    serializer_class = CollegeConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
