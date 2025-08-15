from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Hostel, Room, HostelMember
from django.utils import timezone

User = get_user_model()

class HostelTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(login_id='staff01', password='pass123', is_staff=True)
        self.student = User.objects.create_user(login_id='std01', password='pass123', is_student=True)
        self.hostel = Hostel.objects.create(name='Main Hostel', total_rooms=10)
        self.room = Room.objects.create(hostel=self.hostel, room_number='101', capacity=2, occupants_count=0)
        self.member = HostelMember.objects.create(student=self.student, room=self.room)

    def test_hostel_member_access(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/hostel/members/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
