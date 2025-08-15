from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.admissions.models import AcademicYear, Intake, Application
from apps.academic.models import Program

User = get_user_model()

class AdmissionsFlowTest(APITestCase):
    def setUp(self):
        self.password = "StrongPass!123"
        self.applicant = User.objects.create_user(username="alice", email="alice@test.com", password=self.password)
        self.staff = User.objects.create_user(username="reg1", email="reg1@test.com", password=self.password, is_staff=True)
        # Make staff belong to Admissions group if you use group checks; here we just use is_staff for test simplicity.

        self.ay = AcademicYear.objects.create(
            year="2025/2026",
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date(),
            is_active=True
        )
        self.intake = Intake.objects.create(
            academic_year=self.ay,
            name="September",
            opens_at=timezone.now() - timedelta(days=1),
            closes_at=timezone.now() + timedelta(days=30),
            is_open=True
        )
        self.program = Program.objects.create(name="BSc Computer Science", code="BSC-CS", duration_years=4)

        self.client = APIClient()

    def test_application_submit_issue_accept_offer(self):
        # Applicant creates application
        self.client.login(username="alice", password=self.password)
        res = self.client.post(reverse("admissions-applications-list"), {
            "academic_year": self.ay.id,
            "intake": self.intake.id,
            "program": self.program.id,
            "personal_data": {"address": "Nairobi"},
            "education_history": [{"school": "ABC High", "grade": "A"}]
        }, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        app_id = res.data["id"]

        # Submit should fail due to missing docs
        res = self.client.post(reverse("admissions-applications-submit", args=[app_id]))
        self.assertEqual(res.status_code, 400)
        self.client.logout()

        # Staff uploads docs (simulate via direct model create to skip file IO in unit test)
        app = Application.objects.get(pk=app_id)
        from apps.admissions.models import ApplicationDocument
        ApplicationDocument.objects.create(application=app, doc_type="national_id", file="dummy.txt")
        ApplicationDocument.objects.create(application=app, doc_type="transcript", file="dummy2.txt")

        # Applicant submits successfully now
        self.client.login(username="alice", password=self.password)
        res = self.client.post(reverse("admissions-applications-submit", args=[app_id]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "submitted")
        self.client.logout()

        # Staff issues offer
        self.client.login(username="reg1", password=self.password)
        res = self.client.post(reverse("admissions-applications-issue-offer", args=[app_id]), {
            "amount_cents": 10000,
            "expires_at": (timezone.now() + timedelta(days=7)).isoformat()
        }, format="json")
        self.assertEqual(res.status_code, 201, res.content)

        # Applicant accepts offer
        self.client.logout()
        self.client.login(username="alice", password=self.password)
        res = self.client.post(reverse("admissions-applications-accept-offer", args=[app_id]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["accepted_at"] is not None, True)
