import logging
import json
from rest_framework import serializers
from django.utils import timezone
from .models import (
    AcademicYear,
    Intake,
    Application,
    ApplicationDocument,
    ApplicationReview,
    Offer,
    AdmissionDecision,
)
from apps.users.models import User
from apps.academic.models import Program

logger = logging.getLogger(__name__)

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ["id", "year", "start_date", "end_date", "is_active"]

class IntakeSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), source="academic_year", write_only=True
    )

    class Meta:
        model = Intake
        fields = [
            "id",
            "name",
            "academic_year",
            "academic_year_id",
            "opens_at",
            "closes_at",
            "is_open",
        ]

class SubmitApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for the submit action.
    It only handles the status change and validates the transition.
    """
    class Meta:
        model = Application
        fields = ["status"]
        read_only_fields = ["id", "applicant", "program", "intake"]

    def validate_status(self, value):
        if self.instance.status != "draft":
            raise serializers.ValidationError("Only applications with status 'draft' can be submitted.")
        if value != "submitted":
            raise serializers.ValidationError("Status must be 'submitted' to perform this action.")
        return value

    def save(self, **kwargs):
        # Corrected: Use a direct queryset filter instead of assuming the reverse relationship exists.
        required_docs_exist = ApplicationDocument.objects.filter(application=self.instance).exists()
        if not required_docs_exist:
            raise serializers.ValidationError("At least one document is required to submit the application.")
        self.instance.status = "submitted"
        self.instance.submitted_at = timezone.now()
        self.instance.save()
        return self.instance

class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    program = serializers.StringRelatedField(read_only=True)
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), source="program", write_only=True
    )
    intake = IntakeSerializer(read_only=True)
    intake_id = serializers.PrimaryKeyRelatedField(
        queryset=Intake.objects.all(), source="intake", write_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "applicant",
            "program",
            "program_id",
            "intake",
            "intake_id",
            "status",
            "submitted_at",
            "decision_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "submitted_at", "decision_date", "created_at", "updated_at"]

class ApplicationDocumentSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=Application.objects.all(), source="application", write_only=True
    )

    class Meta:
        model = ApplicationDocument
        fields = [
            "id",
            "application",
            "application_id",
            "doc_type",
            "file",
            "meta",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_meta(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as e:
                raise serializers.ValidationError("Meta field must be valid JSON.")
        if not isinstance(value, dict):
            raise serializers.ValidationError("Meta field must be a JSON object.")
        return value

class ApplicationReviewSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=Application.objects.all(), source="application", write_only=True
    )
    reviewer = serializers.StringRelatedField(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="reviewer", write_only=True
    )

    class Meta:
        model = ApplicationReview
        fields = [
            "id",
            "application",
            "application_id",
            "reviewer",
            "reviewer_id",
            "decision",
            "score",
            "comments",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

class IssueOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ["amount_cents", "expires_at"]

    def validate(self, attrs):
        application = self.context.get("application")
        if not application or not isinstance(application, Application):
            raise serializers.ValidationError("Application instance must be provided in the context.")
        
        if application.status not in ["accepted", "under_review"]:
            raise serializers.ValidationError(
                "Offer can only be issued for applications with status 'accepted' or 'under_review'."
            )
        
        # Check for an existing offer to prevent duplicates
        if hasattr(application, 'offer'):
            raise serializers.ValidationError("An offer for this application already exists.")
            
        return attrs

    def create(self, validated_data):
        application = self.context.get("application")
        offered_by = self.context.get("request").user
        validated_data["application"] = application
        validated_data["offered_by"] = offered_by
        return super().create(validated_data)

class AcceptOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ["id", "accepted_at"]
        read_only_fields = ["id", "accepted_at"]

    def validate(self, attrs):
        application = self.context["application"]
        try:
            offer = application.offer
        except Offer.DoesNotExist:
            raise serializers.ValidationError("No offer exists for this application.")
        
        if offer.accepted_at or offer.declined_at:
            raise serializers.ValidationError("Offer has already been accepted or declined.")
        
        if offer.expires_at < timezone.now().date():
            raise serializers.ValidationError("Offer has expired.")
        
        return attrs

    def save(self, **kwargs):
        application = self.context["application"]
        offer = application.offer
        offer.accepted_at = timezone.now()
        offer.save()
        application.status = "offer_accepted"
        application.save()
        return offer

class DeclineOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ["id", "declined_at"]
        read_only_fields = ["id", "declined_at"]

    def validate(self, attrs):
        application = self.context["application"]
        try:
            offer = application.offer
        except Offer.DoesNotExist:
            raise serializers.ValidationError("No offer exists for this application.")
        
        if offer.accepted_at or offer.declined_at:
            raise serializers.ValidationError("Offer has already been accepted or declined.")
        
        if offer.expires_at < timezone.now().date():
            raise serializers.ValidationError("Offer has expired.")
        
        return attrs

    def save(self, **kwargs):
        application = self.context["application"]
        offer = application.offer
        offer.declined_at = timezone.now()
        offer.save()
        application.status = "offer_declined"
        application.save()
        return offer

class OfferSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    offered_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "application",
            "amount_cents",
            "expires_at",
            "issued_at",
            "accepted_at",
            "declined_at",
            "offered_by",
        ]
        read_only_fields = ["id", "issued_at", "accepted_at", "declined_at", "offered_by"]

class AdmissionDecisionSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=Application.objects.all(), source="application", write_only=True
    )
    decided_by = serializers.StringRelatedField(read_only=True)
    decided_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="decided_by", write_only=True
    )

    class Meta:
        model = AdmissionDecision
        fields = [
            "id",
            "application",
            "application_id",
            "decided_by",
            "decided_by_id",
            "decision",
            "remarks",
            "decided_at",
        ]
        read_only_fields = ["id", "decided_at"]