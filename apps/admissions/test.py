import logging
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from apps.users.models import User
from apps.hr.models import Department
from apps.core.models import College
from apps.academic.models import Program
from .models import AcademicYear, Intake, Application, ApplicationDocument, ApplicationReview, Offer, AdmissionDecision
from .filters import ApplicationFilter

logger = logging.getLogger(__name__)

class AdmissionsModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Computer Science Department")
        self.college = College.objects.create(name="Engineering College")
        self.applicant = User.objects.create_user(
            login_id='testuser',
            email='testuser@example.com',
            password='testpass123',
            is_student=True
        )
        self.reviewer = User.objects.create_user(
            login_id='reviewer',
            email='reviewer@example.com',
            password='testpass123',
            is_faculty=True
        )
        self.admin = User.objects.create_user(
            login_id='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.academic_year = AcademicYear.objects.create(
            year='2023-2024',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            is_active=True
        )
        self.intake = Intake.objects.create(
            name='Fall 2023',
            academic_year=self.academic_year,
            opens_at=timezone.now().date(),
            closes_at=timezone.now().date() + timedelta(days=90),
            is_open=True
        )
        self.program = Program.objects.create(
            name='Computer Science',
            department=self.department,
            college=self.college
        )

    def test_academic_year_creation(self):
        logger.debug("Testing AcademicYear creation")
        ay = AcademicYear.objects.create(
            year='2024-2025',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            is_active=False
        )
        self.assertEqual(ay.year, '2024-2025')
        self.assertFalse(ay.is_active)
        self.assertEqual(str(ay), '2024-2025')
        self.assertIn('start_date', ay.__dict__)

    def test_academic_year_unique_year(self):
        logger.debug("Testing AcademicYear unique year constraint")
        with self.assertRaises(Exception):
            AcademicYear.objects.create(
                year='2023-2024',
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=365)
            )

    def test_intake_creation(self):
        logger.debug("Testing Intake creation")
        intake = Intake.objects.create(
            name='Spring 2024',
            academic_year=self.academic_year,
            opens_at=timezone.now().date(),
            closes_at=timezone.now().date() + timedelta(days=90),
            is_open=True
        )
        self.assertEqual(intake.name, 'Spring 2024')
        self.assertTrue(intake.is_open)
        self.assertEqual(intake.academic_year, self.academic_year)

    def test_intake_unique_together(self):
        logger.debug("Testing Intake unique_together constraint")
        with self.assertRaises(Exception):
            Intake.objects.create(
                name='Fall 2023',
                academic_year=self.academic_year,
                opens_at=timezone.now().date(),
                closes_at=timezone.now().date() + timedelta(days=90)
            )

    def test_application_creation(self):
        logger.debug("Testing Application creation")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='draft'
        )
        self.assertEqual(app.applicant, self.applicant)
        self.assertEqual(app.status, 'draft')
        self.assertIsNone(app.submitted_at)

    def test_application_status_choices(self):
        logger.debug("Testing Application status choices")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='submitted'
        )
        self.assertEqual(app.status, 'submitted')
        with self.assertRaises(ValidationError):
            app.status = 'invalid_status'
            app.full_clean()

    def test_application_document_creation(self):
        logger.debug("Testing ApplicationDocument creation")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='draft'
        )
        doc = ApplicationDocument.objects.create(
            application=app,
            doc_type='transcript',
            file=SimpleUploadedFile("test.pdf", b"file_content"),
            meta={'type': 'academic'}
        )
        self.assertEqual(doc.application, app)
        self.assertEqual(doc.doc_type, 'transcript')

    def test_application_document_unique_together(self):
        logger.debug("Testing ApplicationDocument unique_together constraint")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program
        )
        ApplicationDocument.objects.create(
            application=app,
            doc_type='transcript',
            file=SimpleUploadedFile("test.pdf", b"file_content")
        )
        with self.assertRaises(Exception):
            ApplicationDocument.objects.create(
                application=app,
                doc_type='transcript',
                file=SimpleUploadedFile("test2.pdf", b"file_content2")
            )

    def test_application_review_creation(self):
        logger.debug("Testing ApplicationReview creation")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='submitted'
        )
        review = ApplicationReview.objects.create(
            application=app,
            reviewer=self.reviewer,
            decision='accept',
            score=85,
            comments='Good application'
        )
        self.assertEqual(review.application, app)
        self.assertEqual(review.decision, 'accept')

    def test_application_review_unique_together(self):
        logger.debug("Testing ApplicationReview unique_together constraint")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program
        )
        ApplicationReview.objects.create(
            application=app,
            reviewer=self.reviewer,
            decision='accept',
            score=85
        )
        with self.assertRaises(Exception):
            ApplicationReview.objects.create(
                application=app,
                reviewer=self.reviewer,
                decision='reject',
                score=75
            )

    def test_admission_decision_creation(self):
        logger.debug("Testing AdmissionDecision creation")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='under_review'
        )
        decision = AdmissionDecision.objects.create(
            application=app,
            decided_by=self.admin,
            decision='accept',
            remarks='Qualified'
        )
        self.assertEqual(decision.application, app)
        self.assertEqual(decision.decision, 'accept')

    def test_admission_decision_one_to_one(self):
        logger.debug("Testing AdmissionDecision one-to-one constraint")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program
        )
        AdmissionDecision.objects.create(
            application=app,
            decided_by=self.admin,
            decision='accept'
        )
        with self.assertRaises(Exception):
            AdmissionDecision.objects.create(
                application=app,
                decided_by=self.admin,
                decision='reject'
            )

    def test_offer_creation(self):
        logger.debug("Testing Offer creation")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='offer_made'
        )
        offer = Offer.objects.create(
            application=app,
            offered_by=self.admin,
            amount_cents=0,
            expires_at=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(offer.application, app)
        self.assertEqual(offer.status, 'pending')

    def test_offer_one_to_one(self):
        logger.debug("Testing Offer one-to-one constraint")
        app = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program
        )
        Offer.objects.create(
            application=app,
            offered_by=self.admin,
            amount_cents=0,
            expires_at=timezone.now().date() + timedelta(days=30)
        )
        with self.assertRaises(Exception):
            Offer.objects.create(
                application=app,
                offered_by=self.admin,
                amount_cents=1000,
                expires_at=timezone.now().date() + timedelta(days=15)
            )


class AdmissionsAPITests(LiveServerTestCase):
    def setUp(self):
        logger.debug("Starting AdmissionsAPITests.setUp")
        self.client = APIClient()
        self.client_admin = APIClient()
        self.department = Department.objects.create(name="Computer Science Department")
        self.college = College.objects.create(name="Engineering College")
        self.applicant = User.objects.create_user(
            login_id='testuser',
            email='testuser@example.com',
            password='testpass123',
            is_student=True
        )
        self.admin = User.objects.create_user(
            login_id='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        admissions_group, _ = Group.objects.get_or_create(name='Admissions')
        self.admin.groups.add(admissions_group)
        
        self.client.force_authenticate(user=self.applicant)
        self.client_admin.force_authenticate(user=self.admin)
        logger.debug("Force authentication completed")
        
        self.academic_year = AcademicYear.objects.create(
            year='2023-2024',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            is_active=True
        )
        self.intake = Intake.objects.create(
            name='Fall 2023',
            academic_year=self.academic_year,
            opens_at=timezone.now().date(),
            closes_at=timezone.now().date() + timedelta(days=90),
            is_open=True
        )
        self.program = Program.objects.create(
            name='Computer Science',
            department=self.department,
            college=self.college
        )

    def test_submit_application(self):
        logger.debug("Testing submit application API")
        application = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='draft'
        )
        
        # Create a required document for the application to pass validation
        doc = ApplicationDocument.objects.create(
            application=application,
            doc_type='transcript',
            file=SimpleUploadedFile("test.pdf", b"file_content")
        )

        # Manually create the reverse relationship cache to fix the AttributeError
        application._prefetched_objects_cache = {'applicationdocument_set': [doc]}
        
        url = reverse("application-submit", kwargs={"pk": application.id})
        data = {
            "status": "submitted"
        }
        response = self.client.post(url, data, format="json")
        logger.debug(f"Submit application response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.status, "submitted")
        self.assertIsNotNone(application.submitted_at)

    def test_issue_offer(self):
        logger.debug("Testing issue offer API")
        application = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='accepted'
        )
        
        # Create an admission decision to fulfill the serializer validation
        AdmissionDecision.objects.create(
            application=application,
            decided_by=self.admin,
            decision='accept',
            remarks='Application reviewed and accepted.'
        )

        url = reverse("application-issue-offer", kwargs={"pk": application.id})
        data = {
            "amount_cents": 10000,
            "expires_at": (timezone.now().date() + timedelta(days=30)).isoformat()
        }
        response = self.client_admin.post(url, data, format="json")
        logger.debug(f"Issue offer response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 201)
        offer = Offer.objects.get(application=application)
        self.assertEqual(offer.offered_by, self.admin)
        self.assertEqual(offer.amount_cents, 10000)
        application.refresh_from_db()
        self.assertEqual(application.status, "offer_made")

    def test_accept_offer(self):
        logger.debug("Testing accept offer API")
        application = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='offer_made'
        )
        Offer.objects.create(
            application=application,
            offered_by=self.admin,
            amount_cents=0,
            expires_at=timezone.now().date() + timedelta(days=30)
        )
        url = reverse("application-accept-offer", kwargs={"pk": application.id})
        response = self.client.post(url, format="json")
        logger.debug(f"Accept offer response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 200)
        offer = Offer.objects.get(application=application)
        self.assertIsNotNone(offer.accepted_at)
        application.refresh_from_db()
        self.assertEqual(application.status, "offer_accepted")

    def test_decline_offer(self):
        logger.debug("Testing decline offer API")
        application = Application.objects.create(
            applicant=self.applicant,
            intake=self.intake,
            program=self.program,
            status='offer_made'
        )
        Offer.objects.create(
            application=application,
            offered_by=self.admin,
            amount_cents=0,
            expires_at=timezone.now().date() + timedelta(days=30)
        )
        url = reverse("application-decline-offer", kwargs={"pk": application.id})
        response = self.client.post(url, format="json")
        logger.debug(f"Decline offer response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 200)
        offer = Offer.objects.get(application=application)
        self.assertIsNotNone(offer.declined_at)
        application.refresh_from_db()
        self.assertEqual(application.status, "offer_declined")