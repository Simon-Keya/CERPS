import logging
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from apps.users.models import User
from .models import Book, LibraryMember, BorrowRecord, Category
from .serializers import BorrowRecordSerializer, BookSerializer

logger = logging.getLogger(__name__)

class LibraryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            login_id='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.library_staff_group, _ = Group.objects.get_or_create(name='LibraryStaff')
        self.staff_user.groups.add(self.library_staff_group)

        self.member = LibraryMember.objects.create(user=self.user)
        self.category = Category.objects.create(name='Fiction')
        self.book = Book.objects.create(
            isbn='978-3-16-148410-0',
            title='The Great Gatsby',
            author='F. Scott Fitzgerald',
            copies_total=5,
            copies_available=5,
            category=self.category
        )

    def test_book_creation(self):
        """Test that a book can be created correctly."""
        new_book = Book.objects.create(
            isbn='111-2-22-333333-4',
            title='1984',
            author='George Orwell',
            copies_total=10,
            copies_available=10
        )
        self.assertEqual(new_book.title, '1984')
        self.assertEqual(new_book.copies_available, 10)

    def test_borrow_record_overdue_property(self):
        """Test the is_overdue property of a borrow record."""
        # Create a record that's due in the past
        past_due_date = timezone.now() - timedelta(days=1)
        borrow_record = BorrowRecord.objects.create(
            member=self.member,
            book=self.book,
            due_date=past_due_date
        )
        self.assertTrue(borrow_record.is_overdue)

        # Create a record that's not overdue with a unique borrowed_on timestamp
        future_due_date = timezone.now() + timedelta(days=14)
        not_overdue_record = BorrowRecord.objects.create(
            member=self.member,
            book=self.book,
            due_date=future_due_date,
            borrowed_on=timezone.now() + timedelta(seconds=1) # The fix for the unique constraint
        )
        self.assertFalse(not_overdue_record.is_overdue)

    def test_borrow_and_return_logic(self):
        """Test that borrowing decreases and returning increases copies available."""
        initial_available = self.book.copies_available
        self.assertEqual(initial_available, 5)

        data = {'member': self.member.id, 'book': self.book.id, 'due_date': timezone.now() + timedelta(days=14)}
        serializer = BorrowRecordSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        borrow_record = serializer.save()

        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, initial_available - 1)

        borrow_record.returned_on = timezone.now()
        borrow_record.book.copies_available += 1
        borrow_record.save()
        borrow_record.book.save()
        self.book.refresh_from_db()

        self.assertEqual(self.book.copies_available, initial_available)

class LibraryAPITests(LiveServerTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            login_id='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            login_id='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.library_staff_group, _ = Group.objects.get_or_create(name='LibraryStaff')
        self.staff_user.groups.add(self.library_staff_group)

        self.member = LibraryMember.objects.create(user=self.user)
        self.book = Book.objects.create(
            isbn='978-3-16-148410-0',
            title='The Great Gatsby',
            author='F. Scott Fitzgerald',
            copies_total=5,
            copies_available=5
        )

        self.client.force_authenticate(user=self.user)
        self.staff_client = APIClient()
        self.staff_client.force_authenticate(user=self.staff_user)

    def test_list_books(self):
        """Test that any authenticated user can list books."""
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'The Great Gatsby')

    def test_staff_can_create_book(self):
        """Test that staff can create a new book via the API."""
        url = reverse('book-list')
        data = {
            'isbn': '978-0-12-345678-9',
            'title': 'Test Book',
            'author': 'Test Author',
            'copies_total': 1,
            'copies_available': 1
        }
        response = self.staff_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_user_cannot_create_book(self):
        """Test that a non-staff user cannot create a book."""
        url = reverse('book-list')
        data = {
            'isbn': '978-0-12-345678-9',
            'title': 'Forbidden Book',
            'author': 'Unknown',
            'copies_total': 1,
            'copies_available': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_borrow_record(self):
        """Test that staff can create a borrow record."""
        url = reverse('borrowrecord-list')
        data = {
            'member': self.member.id,
            'book': self.book.id,
            'due_date': timezone.now() + timedelta(days=14)
        }
        initial_copies = self.book.copies_available
        response = self.staff_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BorrowRecord.objects.count(), 1)
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, initial_copies - 1)

    def test_staff_can_return_book(self):
        """Test that staff can return a book via the custom action."""
        borrow_record = BorrowRecord.objects.create(
            member=self.member,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14)
        )
        self.book.copies_available -= 1
        self.book.save()
        
        initial_copies = self.book.copies_available
        url = reverse('borrowrecord-return-book', kwargs={'pk': borrow_record.id})
        response = self.staff_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        borrow_record.refresh_from_db()
        self.assertIsNotNone(borrow_record.returned_on)
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, initial_copies + 1)