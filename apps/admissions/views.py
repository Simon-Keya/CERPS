from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import AcademicYear, Intake, Application, ApplicationDocument, ApplicationReview, Offer, AdmissionDecision
from .serializers import (
    AcademicYearSerializer, IntakeSerializer, ApplicationSerializer, ApplicationDocumentSerializer,
    ApplicationReviewSerializer, SubmitApplicationSerializer, IssueOfferSerializer,
    OfferSerializer, AcceptOfferSerializer, DeclineOfferSerializer, AdmissionDecisionSerializer
)
from .permissions import IsAdmissionsStaff


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
    filterset_fields = ["academic_year", "is_open"]
    search_fields = ["name", "academic_year__year"]
    ordering = ["-opens_at"]


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Applicants can create DRAFT applications for themselves; only Admissions staff can modify others.
    Submit action enforces required docs & intake window.
    """
    queryset = Application.objects.select_related("applicant", "academic_year", "intake", "program").all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "program", "intake", "academic_year", "applicant"]
    search_fields = ["applicant__username", "applicant__email"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.groups.filter(name__in={"Admissions", "Registrar", "SuperAdmin"}).exists():
            return qs
        # applicants only see their own
        return qs.filter(applicant=user)

    def perform_create(self, serializer):
        # Applicant creating for self; staff can set applicant explicitly
        if not (self.request.user.is_superuser or self.request.user.groups.filter(name__in={"Admissions", "Registrar", "SuperAdmin"}).exists()):
            serializer.save(applicant=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        app = self.get_object()
        # Ownership check for non-staff
        if not (request.user.is_superuser or request.user.groups.filter(name__in={"Admissions", "Registrar", "SuperAdmin"}).exists()):
            if app.applicant_id != request.user.id:
                return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        ser = SubmitApplicationSerializer(context={"application": app})
        ser.save()
        return Response(ApplicationSerializer(app, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="issue-offer", permission_classes=[permissions.IsAuthenticated, IsAdmissionsStaff])
    def issue_offer(self, request, pk=None):
        app = self.get_object()
        ser = IssueOfferSerializer(data=request.data, context={"request": request, "application": app})
        ser.is_valid(raise_exception=True)
        offer = ser.save()
        return Response(OfferSerializer(offer).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="accept-offer")
    def accept_offer(self, request, pk=None):
        app = self.get_object()
        ser = AcceptOfferSerializer(data={}, context={"request": request, "application": app})
        ser.is_valid(raise_exception=True)
        offer = ser.save()
        return Response(OfferSerializer(offer).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="decline-offer")
    def decline_offer(self, request, pk=None):
        app = self.get_object()
        ser = DeclineOfferSerializer(data={}, context={"request": request, "application": app})
        ser.is_valid(raise_exception=True)
        offer = ser.save()
        return Response(OfferSerializer(offer).data, status=status.HTTP_200_OK)


class ApplicationDocumentViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDocument.objects.select_related("application").all()
    serializer_class = ApplicationDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmissionsStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["application", "doc_type"]
    ordering = ["-uploaded_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.groups.filter(name__in={"Admissions", "Registrar", "SuperAdmin"}).exists():
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
