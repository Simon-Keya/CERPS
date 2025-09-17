
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcademicYearViewSet,
    IntakeViewSet,
    ApplicationViewSet,
    ApplicationDocumentViewSet,
    ApplicationReviewViewSet,
    OfferViewSet,
    AdmissionDecisionViewSet
)

router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'intakes', IntakeViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'documents', ApplicationDocumentViewSet)
router.register(r'reviews', ApplicationReviewViewSet)
router.register(r'offers', OfferViewSet)
router.register(r'decisions', AdmissionDecisionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]