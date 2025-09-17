from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import JSONField as DJJSONField


class AcademicYear(models.Model):
    """
    Represents an academic year (e.g., 2024/2025).
    """
    year = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.year


class Intake(models.Model):
    """
    Represents an intake/semester admission cycle within an academic year.
    """
    name = models.CharField(max_length=100)
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name="intakes"
    )
    opens_at = models.DateField()
    closes_at = models.DateField()
    is_open = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "academic_year")
        ordering = ["-opens_at"]

    def __str__(self):
        return f"{self.name} - {self.academic_year.year}"


class Application(models.Model):
    """
    Student application for admission to a program in a given intake.
    """
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("offer_made", "Offer Made"),
        ("offer_accepted", "Offer Accepted"),
        ("offer_declined", "Offer Declined"),
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    intake = models.ForeignKey(
        Intake, on_delete=models.CASCADE, related_name="applications"
    )
    # Changed from CharField to ForeignKey
    program = models.ForeignKey(
        'academic.Program', on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="draft")
    submitted_at = models.DateTimeField(null=True, blank=True)
    decision_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.applicant} - {self.program.name} ({self.intake})"


class ApplicationDocument(models.Model):
    """
    Stores metadata about uploaded documents for applications.
    """
    DOC_TYPES = [
        ("national_id", "National ID/Passport"),
        ("transcript", "Transcript"),
        ("certificate", "Certificate"),
        ("photo", "Passport Photo"),
        ("other", "Other"),
    ]

    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="documents"
    )
    doc_type = models.CharField(max_length=32, choices=DOC_TYPES)
    file = models.FileField(upload_to="admissions/docs/%Y/%m/")
    meta = DJJSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("application", "doc_type")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.application_id} - {self.doc_type}"


class ApplicationReview(models.Model):
    """
    Represents a review of an application by an admissions officer/staff.
    """
    DECISION_CHOICES = [
        ("accept", "Accept"),
        ("reject", "Reject"),
        ("waitlist", "Waitlist"),
    ]

    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="application_reviews",
    )
    decision = models.CharField(max_length=32, choices=DECISION_CHOICES)
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("application", "reviewer")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review for {self.application} by {self.reviewer}"


class AdmissionDecision(models.Model):
    """
    Final decision made on an application (consolidated after reviews).
    """
    DECISION_CHOICES = [
        ("accept", "Accept"),
        ("reject", "Reject"),
        ("waitlist", "Waitlist"),
    ]

    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name="final_decision"
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="decisions_made",
    )
    decision = models.CharField(max_length=32, choices=DECISION_CHOICES)
    remarks = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application} - {self.decision}"


class Offer(models.Model):
    """
    Represents an admission offer made to a student after acceptance.
    """
    OFFER_STATUS = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("expired", "Expired"),
    ]

    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name="offer"
    )
    offered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="offers_made",
    )
    amount_cents = models.PositiveIntegerField(default=0)
    expires_at = models.DateField()
    issued_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)

    @property
    def status(self):
        if self.accepted_at:
            return "accepted"
        elif self.declined_at:
            return "declined"
        elif self.expires_at < timezone.now().date():
            return "expired"
        else:
            return "pending"

    def __str__(self):
        return f"Offer for {self.application} - {self.status}"