from rest_framework import serializers
from .models import Department, AcademicYear, Program, GradingScale, CollegeConfig

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source='department', write_only=True)

    class Meta:
        model = Program
        fields = ['id', 'name', 'code', 'duration_years', 'department', 'department_id']

class GradingScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingScale
        fields = '__all__'

class CollegeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeConfig
        fields = '__all__'
