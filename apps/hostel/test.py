import logging
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from apps.users.models import User
from .models import Hostel, Floor, Room, Bed, Student, Booking, Complaint
from .filters import RoomFilter, BookingFilter

logger = logging.getLogger(__name__)

# This class should only test model logic and database interactions.
# It should not use APIClient or live server features.
class HostelModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            login_id='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.hostel = Hostel.objects.create(
            name='Main Hostel',
            address='123 Campus Road',
            capacity=100
        )
        self.floor = Floor.objects.create(
            hostel=self.hostel,
            number=1
        )
        self.room = Room.objects.create(
            floor=self.floor,
            number='101',
            room_type='single',
            capacity=1
        )
        self.bed = Bed.objects.create(
            room=self.room,
            number='1'
        )
        self.student = Student.objects.create(
            user=self.user,
            registration_number='STU001',
            phone_number='1234567890'
        )

    def test_hostel_creation(self):
        logger.debug("Testing Hostel creation")
        hostel = Hostel.objects.create(
            name='North Hostel',
            address='456 Campus Road',
            capacity=50
        )
        self.assertEqual(hostel.name, 'North Hostel')
        self.assertTrue(hostel.is_active)

    def test_floor_unique_together(self):
        logger.debug("Testing Floor unique_together constraint")
        with self.assertRaises(Exception):
            Floor.objects.create(
                hostel=self.hostel,
                number=1
            )

    def test_room_creation(self):
        logger.debug("Testing Room creation")
        room = Room.objects.create(
            floor=self.floor,
            number='102',
            room_type='double',
            capacity=2
        )
        self.assertEqual(room.number, '102')
        self.assertTrue(room.is_available)

    def test_bed_occupancy(self):
        logger.debug("Testing Bed occupancy")
        self.assertFalse(self.bed.is_occupied)
        booking = Booking.objects.create(
            student=self.student,
            bed=self.bed,
            start_date=timezone.now().date()
        )
        booking.status = 'confirmed'
        booking.save()
        self.bed.refresh_from_db()
        self.assertTrue(self.bed.is_occupied)

    def test_booking_status(self):
        logger.debug("Testing Booking status")
        booking = Booking.objects.create(
            student=self.student,
            bed=self.bed,
            start_date=timezone.now().date(),
            status='pending'
        )
        self.assertEqual(booking.status, 'pending')
        booking.status = 'confirmed'
        booking.save()
        self.bed.refresh_from_db()
        self.assertTrue(self.bed.is_occupied)

    # Removed the API-related tests from this class
    # and moved them to HostelAPITests below.

# This class should handle all API-related tests.
class HostelAPITests(LiveServerTestCase):
    def setUp(self):
        logger.debug("Starting HostelAPITests.setUp")
        self.client = APIClient()
        self.client_admin = APIClient()
        self.user = User.objects.create_user(
            login_id='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            login_id='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        hostel_group, _ = Group.objects.get_or_create(name='HostelAdmin')
        self.admin.groups.add(hostel_group)
        self.client.force_authenticate(user=self.user)
        self.client_admin.force_authenticate(user=self.admin)
        self.hostel = Hostel.objects.create(
            name='Main Hostel',
            address='123 Campus Road',
            capacity=100
        )
        self.floor = Floor.objects.create(
            hostel=self.hostel,
            number=1
        )
        self.room = Room.objects.create(
            floor=self.floor,
            number='101',
            room_type='single',
            capacity=1
        )
        self.bed = Bed.objects.create(
            room=self.room,
            number='1'
        )
        self.student = Student.objects.create(
            user=self.user,
            registration_number='STU001',
            phone_number='1234567890'
        )

    def test_create_hostel(self):
        logger.debug("Testing create hostel API")
        url = reverse('hostel-list')
        data = {
            'name': 'South Hostel',
            'address': '789 Campus Road',
            'capacity': 50
        }
        response = self.client_admin.get(url)
        self.client_admin.credentials(HTTP_X_CSRFTOKEN=response.wsgi_request.COOKIES.get('csrftoken', ''))
        response = self.client_admin.post(url, data, format='json')
        logger.debug(f"Create hostel response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Hostel.objects.count(), 2)
        self.assertEqual(Hostel.objects.last().name, 'South Hostel')

    def test_create_booking(self):
        logger.debug("Testing create booking API")
        url = reverse('booking-create-booking')
        data = {
            'bed': self.bed.id,
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=365)).isoformat()
        }
        response = self.client.get(url)
        self.client.credentials(HTTP_X_CSRFTOKEN=response.wsgi_request.COOKIES.get('csrftoken', ''))
        response = self.client.post(url, data, format='json')
        logger.debug(f"Create booking response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 201)
        booking = Booking.objects.get(bed=self.bed)
        self.assertEqual(booking.student, self.student)
        self.assertEqual(booking.status, 'pending')

    def test_create_complaint(self):
        logger.debug("Testing create complaint API")
        url = reverse('complaint-list')
        data = {
            'title': 'Room Issue',
            'description': 'Broken window',
            'status': 'open'
        }
        response = self.client.get(url)
        self.client.credentials(HTTP_X_CSRFTOKEN=response.wsgi_request.COOKIES.get('csrftoken', ''))
        response = self.client.post(url, data, format='json')
        logger.debug(f"Create complaint response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 201)
        complaint = Complaint.objects.get(student=self.student)
        self.assertEqual(complaint.title, 'Room Issue')

    def test_resolve_complaint(self):
        logger.debug("Testing resolve complaint API")
        complaint = Complaint.objects.create(
            student=self.student,
            title='Room Issue',
            description='Broken window',
            status='open'
        )
        url = reverse('complaint-resolve-complaint', kwargs={'pk': complaint.id})
        response = self.client_admin.get(url)
        self.client_admin.credentials(HTTP_X_CSRFTOKEN=response.wsgi_request.COOKIES.get('csrftoken', ''))
        response = self.client_admin.post(url, {}, format='json')
        logger.debug(f"Resolve complaint response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 200)
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, 'resolved')
        self.assertIsNotNone(complaint.resolved_at)