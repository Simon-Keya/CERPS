from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(login_id='std01', password='pass123', is_student=True)
        self.client.force_authenticate(user=self.user)
        self.notif = Notification.objects.create(recipient=self.user, title="Test", message="Hello", notif_type="EMAIL")

    def test_list_notifications(self):
        response = self.client.get('/api/notifications/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
