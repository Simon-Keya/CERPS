from django.contrib import admin
from .models import *

admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Instructor)
admin.site.register(TeachingAssignment)
admin.site.register(Timetable)
admin.site.register(Grade)
