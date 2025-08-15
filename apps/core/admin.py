from django.contrib import admin
from .models import Department, AcademicYear, Program, GradingScale, CollegeConfig

admin.site.register(Department)
admin.site.register(AcademicYear)
admin.site.register(Program)
admin.site.register(GradingScale)
admin.site.register(CollegeConfig)
