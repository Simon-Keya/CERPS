from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    AcademicYearViewSet, IntakeViewSet, ApplicationViewSet,
    ApplicationDocumentViewSet, ApplicationReviewViewSet, AdmissionDecisionViewSet
)

router = DefaultRouter()
router.register("academic-years", AcademicYearViewSet, basename="admissions-academic-years")
router.register("intakes", IntakeViewSet, basename="admissions-intakes")
router.register("applications", ApplicationViewSet, basename="admissions-applications")
router.register("documents", ApplicationDocumentViewSet, basename="admissions-documents")
router.register("reviews", ApplicationReviewViewSet, basename="admissions-reviews")
router.register("decisions", AdmissionDecisionViewSet, basename="admissions-decisions")

urlpatterns = [
    path("", include(router.urls)),
]
