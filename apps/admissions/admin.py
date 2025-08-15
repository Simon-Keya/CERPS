from django.contrib import admin
from .models import AcademicYear, Intake, Application, ApplicationDocument, ApplicationReview, Offer, AdmissionDecision

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("year", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("year",)


@admin.register(Intake)
class IntakeAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "opens_at", "closes_at", "is_open")
    list_filter = ("is_open", "academic_year")
    search_fields = ("name", "academic_year__year")


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "applicant", "program", "status", "intake", "submitted_at", "created_at")
    list_filter = ("status", "intake__academic_year", "program")
    search_fields = ("applicant__username", "applicant__email", "program__name", "program__code")
    inlines = [ApplicationDocumentInline]
    actions = ["mark_under_review"]

    @admin.action(description="Mark selected applications as Under Review")
    def mark_under_review(self, request, queryset):
        updated = queryset.update(status="under_review")
        self.message_user(request, f"{updated} application(s) marked as Under Review.")


@admin.register(ApplicationReview)
class ApplicationReviewAdmin(admin.ModelAdmin):
    list_display = ("application", "reviewer", "decision", "score", "created_at")
    list_filter = ("decision",)
    search_fields = ("application__id", "reviewer__username")


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("application", "amount_cents", "expires_at", "issued_at", "accepted_at", "declined_at")
    list_filter = ("accepted_at", "declined_at")


@admin.register(AdmissionDecision)
class AdmissionDecisionAdmin(admin.ModelAdmin):
    list_display = ("application", "decision", "decided_by", "decided_at")
    list_filter = ("decision",)
