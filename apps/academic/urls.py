from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProgramViewSet, InstructorViewSet, CourseViewSet, StudentViewSet,
    SubjectViewSet, TimetableViewSet, GradeViewSet, TeachingAssignmentViewSet,
    AcademicYearViewSet # Import the AcademicYearViewSet
)

router = DefaultRouter()
router.register(r'academicyears', AcademicYearViewSet) # Register the new ViewSet
router.register(r'programs', ProgramViewSet)
router.register(r'instructors', InstructorViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'students', StudentViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'timetables', TimetableViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'teaching-assignments', TeachingAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]