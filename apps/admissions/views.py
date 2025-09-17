import logging
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import AcademicYear, Intake, Application, ApplicationDocument, ApplicationReview, Offer, AdmissionDecision
from .serializers import (
    AcademicYearSerializer, IntakeSerializer, ApplicationSerializer, ApplicationDocumentSerializer,
    ApplicationReviewSerializer, SubmitApplicationSerializer, IssueOfferSerializer,
    OfferSerializer, AcceptOfferSerializer, DeclineOfferSerializer, AdmissionDecisionSerializer
)
from .permissions import IsAdmissionsStaff, IsApplicantOrAdmissionsStaff
from .filters import ApplicationFilter

logger = logging.getLogger(__name__)

class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["year"]
    ordering = ["-start_date"]

class IntakeViewSet(viewsets.ModelViewSet):
    queryset = Intake.objects.select_related("academic_year").all()
    serializer_class = IntakeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["academic_year__year", "is_open"]
    search_fields = ["name", "academic_year__year"]
    ordering = ["-opens_at"]

class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Applicants can create DRAFT applications for themselves; only Admissions staff can modify others.
    Submit action enforces required docs & intake window.
    """
    queryset = Application.objects.select_related("applicant", "intake", "program").all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicantOrAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ApplicationFilter
    search_fields = ["applicant__username", "applicant__email"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        logger.debug(f"ApplicationViewSet.get_queryset for user: {user}")
        if user.groups.filter(name='Admissions').exists():
            return qs
        return qs.filter(applicant=user)

    def perform_create(self, serializer):
        logger.debug(f"ApplicationViewSet.perform_create for user: {self.request.user}")
        if not self.request.user.groups.filter(name='Admissions').exists():
            serializer.save(applicant=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=["post"], url_path="submit", permission_classes=[permissions.IsAuthenticated, IsApplicantOrAdmissionsStaff])
    def submit(self, request, pk=None):
        app = self.get_object()
        ser = SubmitApplicationSerializer(instance=app, data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        app = ser.save()
        return Response(ApplicationSerializer(app, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="issue-offer", permission_classes=[permissions.IsAuthenticated, IsAdmissionsStaff])
    def issue_offer(self, request, pk=None):
        app = self.get_object()
        ser = IssueOfferSerializer(data=request.data, context={"request": request, "application": app})
        ser.is_valid(raise_exception=True)
        offer = ser.save()
        # Explicitly set the application status to 'offer_made'
        app.status = 'offer_made'
        app.save()
        return Response(OfferSerializer(offer).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="accept-offer", permission_classes=[permissions.IsAuthenticated, IsApplicantOrAdmissionsStaff])
    def accept_offer(self, request, pk=None):
        app = self.get_object()
        ser = AcceptOfferSerializer(instance=app.offer, data={}, context={"request": request, "application": app})
        ser.is_valid(raise_exception=True)
        offer = ser.save()
        return Response(OfferSerializer(offer).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="decline-offer", permission_classes=[permissions.IsAuthenticated, IsApplicantOrAdmissionsStaff])
    def decline_offer(self, request, pk=None):
        app = self.get_object()
        ser = DeclineOfferSerializer(instance=app.offer, data={}, context={"request": request, "application": app})
        ser.is_valid(raise_exception=True)
        offer = ser.save()
        return Response(OfferSerializer(offer).data, status=status.HTTP_200_OK)

class ApplicationDocumentViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDocument.objects.select_related("application").all()
    serializer_class = ApplicationDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicantOrAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["application", "doc_type"]
    ordering = ["-uploaded_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        logger.debug(f"ApplicationDocumentViewSet.get_queryset for user: {user}")
        if user.groups.filter(name='Admissions').exists():
            return qs
        return qs.filter(application__applicant=user)

class ApplicationReviewViewSet(viewsets.ModelViewSet):
    queryset = ApplicationReview.objects.select_related("application", "reviewer").all()
    serializer_class = ApplicationReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["application", "decision"]
    ordering = ["-created_at"]

class AdmissionDecisionViewSet(viewsets.ModelViewSet):
    queryset = AdmissionDecision.objects.select_related("application", "decided_by").all()
    serializer_class = AdmissionDecisionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["decision"]
    ordering = ["-decided_at"]

    def perform_create(self, serializer):
        serializer.save(decided_by=self.request.user)

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.select_related("application", "offered_by").all()
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicantOrAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["application", "status"]
    ordering = ["-issued_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        logger.debug(f"OfferViewSet.get_queryset for user: {user}")
        if user.groups.filter(name='Admissions').exists():
            return qs
        return qs.filter(application__applicant=user)