from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField, JSONField  # Django 5 supports JSONField directly

# If you don't use Postgres, swap JSONField import for models.JSONField
try:
    from django.db.models import JSONField as DJJSONField
except Exception:
    DJJSONField = JSONField

# External dependency on Academic app
try:
    from apps.academic.models import Program
except Exception:
    Program = None  # to avoid import errors at code-time; migrations/runtime should have it


class AcademicYear(models.Model):
    """
    e.g., 2025/2026. Exactly one active at a time (recommended).
    """
    year = models.CharField(max_length=9, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("AcademicYear.start_date must be before end_date")

    def __str__(self) -> str:
        return self.year


class Intake(models.Model):
    """
    Application window within an academic year (e.g., Jan Intake, Sep Intake).
    """
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="intakes")
    name = models.CharField(max_length=50)  # e.g., "September"
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    is_open = models.BooleanField(default=True)

    class Meta:
        unique_together = [("academic_year", "name")]
        ordering = ["-opens_at"]

    def clean(self):
        if self.opens_at >= self.closes_at:
            raise ValidationError("Intake.opens_at must be before closes_at")

    def __str__(self):
        return f"{self.academic_year.year} - {self.name}"


class Application(models.Model):
    """
    A single application to a Program during an Intake.
    Each user/applicant can submit multiple applications across years/programs, but one per program/intake.
    """
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        OFFERED = "offered", "Offered"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        REJECTED = "rejected", "Rejected"
        ENROLLED = "enrolled", "Enrolled"

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="applications")
    intake = models.ForeignKey(Intake, on_delete=models.PROTECT, related_name="applications")
    program = models.ForeignKey("academic.Program", on_delete=models.PROTECT, related_name="applications")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    personal_data = DJJSONField(default=dict, blank=True)  # e.g., {bio, address, guardian, etc}
    education_history = DJJSONField(default=list, blank=True)  # list of dicts
    meta = DJJSONField(default=dict, blank=True)  # extra attributes
    submitted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("applicant", "intake", "program")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id} - {self.applicant} - {self.program} ({self.status})"

    def can_submit(self) -> bool:
        now = timezone.now()
        return self.status == self.Status.DRAFT and self.intake.opens_at <= now <= self.intake.closes_at and self.intake.is_open

    def can_review(self) -> bool:
        return self.status in {self.Status.SUBMITTED, self.Status.UNDER_REVIEW}

    def can_offer(self) -> bool:
        return self.status in {self.Status.SUBMITTED, self.Status.UNDER_REVIEW}

    def can_accept_offer(self) -> bool:
        return self.status == self.Status.OFFERED

    def can_decline_offer(self) -> bool:
        return self.status == self.Status.OFFERED

    def can_enroll(self) -> bool:
        return self.status == self.Status.ACCEPTED

    @transaction.atomic
    def submit(self):
        if not self.can_submit():
            raise ValidationError("Application cannot be submitted in its current state or intake is closed.")
        # ensure required docs are present
        missing = self.missing_required_documents()
        if missing:
            raise ValidationError(f"Missing required documents: {', '.join(missing)}")
        self.status = self.Status.SUBMITTED
        self.submitted_at = timezone.now()
        self.save(update_fields=["status", "submitted_at", "updated_at"])

    def required_documents(self):
        """
        You can expand this to fetch from Program config.
        For now, enforce ID + Transcript.
        """
        return {"national_id", "transcript"}

    def missing_required_documents(self):
        provided = set(self.documents.values_list("doc_type", flat=True))
        return [d for d in self.required_documents() if d not in provided]


class ApplicationDocument(models.Model):
    """
    Stores metadata about uploaded docs. Actual file storage can be a FileField or external storage.
    """
    DOC_TYPES = [
        ("national_id", "National ID/Passport"),
        ("transcript", "Transcript"),
        ("certificate", "Certificate"),
        ("photo", "Passport Photo"),
        ("other", "Other"),
    ]
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=32, choices=DOC_TYPES)
    file = models.FileField(upload_to="admissions/docs/%Y/%m/")  # configure MEDIA
    meta = DJJSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("application", "doc_type")]  # 1 type each, adjust if multiples allowed

    def __str__(self):
        return f"{self.application_id} - {self.doc_type}"


class ApplicationReview(models.Model):
    """
    Staff review with rubric scoring.
    """
    DECISIONS = [
        ("pending", "Pending"),
        ("recommend_offer", "Recommend Offer"),
        ("recommend_reject", "Recommend Reject"),
    ]
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comments = models.TextField(blank=True)
    decision = models.CharField(max_length=20, choices=DECISIONS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Offer(models.Model):
    """
    An offer issued to the applicant. Accept/Decline drives Application status.
    """
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="offer")
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    amount_cents = models.PositiveIntegerField(default=0)  # deposit/commitment fee if any
    expires_at = models.DateTimeField()
    issued_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    meta = DJJSONField(default=dict, blank=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @transaction.atomic
    def accept(self, by_user):
        if self.is_expired():
            raise ValidationError("Offer has expired.")
        if self.application.status != Application.Status.OFFERED:
            raise ValidationError("Application is not in OFFERED status.")
        self.accepted_at = timezone.now()
        self.save(update_fields=["accepted_at"])
        self.application.status = Application.Status.ACCEPTED
        self.application.save(update_fields=["status", "updated_at"])

    @transaction.atomic
    def decline(self, by_user):
        if self.application.status != Application.Status.OFFERED:
            raise ValidationError("Application is not in OFFERED status.")
        self.declined_at = timezone.now()
        self.save(update_fields=["declined_at"])
        self.application.status = Application.Status.DECLINED
        self.application.save(update_fields=["status", "updated_at"])


class AdmissionDecision(models.Model):
    """
    Records a final decision (accept/reject) and reason. (Separate from Offer for auditability.)
    """
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="decision")
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    decision = models.CharField(max_length=20, choices=[("accept", "Accept"), ("reject", "Reject")])
    reason = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    def apply(self):
        """
        Apply final decision to the application if not already reflected.
        """
        if self.decision == "accept" and self.application.status not in (
            Application.Status.ACCEPTED, Application.Status.ENROLLED
        ):
            self.application.status = Application.Status.ACCEPTED
        elif self.decision == "reject":
            self.application.status = Application.Status.REJECTED
        self.application.save(update_fields=["status", "updated_at"])
