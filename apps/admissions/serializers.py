from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import AcademicYear, Intake, Application, ApplicationDocument, ApplicationReview, Offer, AdmissionDecision
from apps.academic.models import Program

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'year', 'start_date', 'end_date', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class IntakeSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), source='academic_year', write_only=True
    )

    class Meta:
        model = Intake
        fields = ['id', 'academic_year', 'academic_year_id', 'name', 'opens_at', 'closes_at', 'is_open', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = ['id', 'doc_type', 'file', 'meta', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), source='academic_year', write_only=True
    )
    intake = IntakeSerializer(read_only=True)
    intake_id = serializers.PrimaryKeyRelatedField(
        queryset=Intake.objects.all(), source='intake', write_only=True
    )
    program = serializers.StringRelatedField(read_only=True)
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), source='program', write_only=True
    )
    documents = ApplicationDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'applicant', 'academic_year', 'academic_year_id', 'intake', 'intake_id',
            'program', 'program_id', 'status', 'personal_data', 'education_history',
            'meta', 'submitted_at', 'updated_at', 'created_at', 'documents'
        ]
        read_only_fields = ['id', 'applicant', 'submitted_at', 'updated_at', 'created_at']

    def validate(self, data):
        if 'status' in data and data['status'] == Application.Status.SUBMITTED:
            if not data.get('intake').is_open:
                raise ValidationError("Cannot submit application for a closed intake.")
        return data

class SubmitApplicationSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('context', {}).get('application')
        super().__init__(*args, **kwargs)

    def validate(self, data):
        if not self.application:
            raise ValidationError("Application context is required.")
        if not self.application.can_submit():
            raise ValidationError("Application cannot be submitted in its current state or intake is closed.")
        missing = self.application.missing_required_documents()
        if missing:
            raise ValidationError(f"Missing required documents: {', '.join(missing)}")
        return data

    def save(self):
        self.application.submit()
        return self.application

class ApplicationReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ApplicationReview
        fields = ['id', 'application', 'reviewer', 'score', 'comments', 'decision', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']

    def validate(self, data):
        if data['application'].status not in (Application.Status.SUBMITTED, Application.Status.UNDER_REVIEW):
            raise ValidationError("Review can only be created for applications in SUBMITTED or UNDER_REVIEW status.")
        return data

class IssueOfferSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=Application.objects.all(), source='application', write_only=True
    )
    issued_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'application', 'application_id', 'issued_by', 'amount_cents', 'expires_at', 'issued_at', 'accepted_at', 'declined_at', 'meta']
        read_only_fields = ['id', 'issued_by', 'issued_at', 'accepted_at', 'declined_at']

    def validate(self, data):
        if not data['application'].can_offer():
            raise ValidationError("Offer can only be issued for applications in SUBMITTED or UNDER_REVIEW status.")
        if 'expires_at' in data and data['expires_at'] <= timezone.now():
            raise ValidationError("Offer expiration date must be in the future.")
        return data

    def create(self, validated_data):
        validated_data['issued_by'] = self.context['request'].user
        offer = Offer.objects.create(**validated_data)
        offer.application.status = Application.Status.OFFERED
        offer.application.save(update_fields=['status', 'updated_at'])
        return offer

class AcceptOfferSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('context', {}).get('application')
        super().__init__(*args, **kwargs)

    def validate(self, data):
        if not self.application:
            raise ValidationError("Application context is required.")
        try:
            offer = self.application.offer
        except Offer.DoesNotExist:
            raise ValidationError("No offer exists for this application.")
        if not offer.application.can_accept_offer():
            raise ValidationError("Offer cannot be accepted in the current application state.")
        if offer.is_expired():
            raise ValidationError("Offer has expired.")
        return data

    def save(self):
        offer = self.application.offer
        offer.accept(self.context['request'].user)
        return offer

class DeclineOfferSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('context', {}).get('application')
        super().__init__(*args, **kwargs)

    def validate(self, data):
        if not self.application:
            raise ValidationError("Application context is required.")
        try:
            offer = self.application.offer
        except Offer.DoesNotExist:
            raise ValidationError("No offer exists for this application.")
        if not offer.application.can_decline_offer():
            raise ValidationError("Offer cannot be declined in the current application state.")
        return data

    def save(self):
        offer = self.application.offer
        offer.decline(self.context['request'].user)
        return offer

class OfferSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=Application.objects.all(), source='application', write_only=True
    )
    issued_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'application', 'application_id', 'issued_by', 'amount_cents', 'expires_at', 'issued_at', 'accepted_at', 'declined_at', 'meta']
        read_only_fields = ['id', 'issued_by', 'issued_at', 'accepted_at', 'declined_at']

class AdmissionDecisionSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=Application.objects.all(), source='application', write_only=True
    )
    decided_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AdmissionDecision
        fields = ['id', 'application', 'application_id', 'decided_by', 'decision', 'reason', 'decided_at']
        read_only_fields = ['id', 'decided_by', 'decided_at']

    def validate(self, data):
        if data['application'].status not in (Application.Status.ACCEPTED, Application.Status.OFFERED):
            raise ValidationError("Decision can only be made for applications in ACCEPTED or OFFERED status.")
        return data

    def create(self, validated_data):
        validated_data['decided_by'] = self.context['request'].user
        decision = AdmissionDecision.objects.create(**validated_data)
        decision.apply()
        return decision