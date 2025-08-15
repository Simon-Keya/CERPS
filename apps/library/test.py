from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Book, LibraryMember, BorrowRecord

User = get_user_model()

class LibraryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(login_id='staff01', password='pass123', is_staff=True)
        self.student_user = User.objects.create_user(login_id='std01', password='pass123', is_student=True)
        self.book = Book.objects.create(isbn='12345', title='Django 101', author='Author A', copies_total=2, copies_available=2)
        self.member = LibraryMember.objects.create(user=self.student_user)

    def test_borrow_book(self):
        self.client.force_authenticate(user=self.staff_user)
        data = {'member': self.member.id, 'book': self.book.id, 'due_date': timezone.now() + timezone.timedelta(days=7)}
        response = self.client.post('/api/library/borrow-records/', data)
        self.assertEqual(response.status_code, 201)
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, 1)

    def test_return_book(self):
        borrow = BorrowRecord.objects.create(member=self.member, book=self.book, due_date=timezone.now() + timezone.timedelta(days=7))
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(f'/api/library/borrow-records/{borrow.id}/return_book/')
        self.assertEqual(response.status_code, 200)
        borrow.refresh_from_db()
        self.assertIsNotNone(borrow.returned_on)
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, self.book.copies_total)
