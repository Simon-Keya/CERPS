from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import Mock
from apps.users.models import User
from apps.academic.models import Student, Program
from apps.hr.models import Department
from apps.finance.models import Ledger, Invoice, Payment
from apps.finance.serializers import LedgerSerializer, InvoiceSerializer, PaymentSerializer
from apps.finance.permissions import IsFinanceAdmin
from datetime import date, timedelta
import json

class FinanceModelTests(TestCase):
    def setUp(self):
        # Create dependencies
        self.department = Department.objects.create(name='Test Dept')
        self.program = Program.objects.create(name='Test Program', department=self.department)
        # Create a test user and student
        self.user = User.objects.create_user(
            login_id='teststudent',
            password='testpass123',
            is_staff=False
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='STU001',
            program=self.program
        )
        self.ledger = Ledger.objects.create(
            student=self.student,
            balance_cents=50000  # $500.00
        )
        self.invoice = Invoice.objects.create(
            ledger=self.ledger,
            amount_cents=10000,  # $100.00
            description='Tuition Fee',
            due_date=date.today() + timedelta(days=30),
            status='pending'
        )
        self.payment = Payment.objects.create(
            invoice=self.invoice,
            amount_cents=5000,  # $50.00
            payment_method='card',
            paid_at=timezone.now()
        )

    def test_ledger_creation(self):
        """Test Ledger model creation and string representation"""
        self.assertEqual(self.ledger.student, self.student)
        self.assertEqual(self.ledger.balance_cents, 50000)
        self.assertTrue(self.ledger.created_at)
        self.assertTrue(self.ledger.updated_at)
        self.assertEqual(
            str(self.ledger),
            f"Ledger for {self.student} - Balance: 500.00"
        )

    def test_invoice_creation(self):
        """Test Invoice model creation and string representation"""
        self.assertEqual(self.invoice.ledger, self.ledger)
        self.assertEqual(self.invoice.amount_cents, 10000)
        self.assertEqual(self.invoice.description, 'Tuition Fee')
        self.assertEqual(self.invoice.status, 'pending')
        self.assertTrue(self.invoice.created_at)
        self.assertTrue(self.invoice.updated_at)
        self.assertEqual(
            str(self.invoice),
            f"Invoice {self.invoice.id} - {self.ledger.student} - 100.00"
        )

    def test_payment_creation(self):
        """Test Payment model creation and string representation"""
        self.assertEqual(self.payment.invoice, self.invoice)
        self.assertEqual(self.payment.amount_cents, 5000)
        self.assertEqual(self.payment.payment_method, 'card')
        self.assertTrue(self.payment.paid_at)
        self.assertTrue(self.payment.created_at)
        self.assertEqual(
            str(self.payment),
            f"Payment {self.payment.id} - {self.invoice} - 50.00"
        )

    def test_ledger_student_relationship(self):
        """Test Ledger foreign key to Student"""
        self.assertEqual(self.ledger.student.user.login_id, 'teststudent')
        self.assertEqual(self.ledger.student.student_id, 'STU001')

    def test_invoice_ledger_relationship(self):
        """Test Invoice foreign key to Ledger"""
        self.assertEqual(self.invoice.ledger.student, self.student)

    def test_payment_invoice_relationship(self):
        """Test Payment foreign key to Invoice"""
        self.assertEqual(self.payment.invoice.ledger, self.ledger)

    def test_invoice_status_choices(self):
        """Test Invoice status choices"""
        valid_statuses = ['pending', 'paid', 'overdue']
        for status in valid_statuses:
            self.invoice.status = status
            self.invoice.save()
            self.assertEqual(self.invoice.status, status)
        
        # Test invalid choice - Django doesn't automatically validate choices
        # We need to use full_clean() to trigger validation
        self.invoice.status = 'invalid'
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()

    def test_payment_method_choices(self):
        """Test Payment method choices"""
        valid_methods = ['cash', 'card', 'bank_transfer']
        for method in valid_methods:
            self.payment.payment_method = method
            self.payment.save()
            self.assertEqual(self.payment.payment_method, method)
        
        # Test invalid choice - use full_clean() to trigger validation
        self.payment.payment_method = 'invalid'
        with self.assertRaises(ValidationError):
            self.payment.full_clean()

    def test_ledger_balance_cents_validation(self):
        """Test Ledger balance_cents can be negative or zero"""
        self.ledger.balance_cents = -10000  # -$100.00
        self.ledger.save()
        self.assertEqual(self.ledger.balance_cents, -10000)
        self.ledger.balance_cents = 0
        self.ledger.save()
        self.assertEqual(self.ledger.balance_cents, 0)

    def test_invoice_amount_cents_validation(self):
        """Test Invoice amount_cents must be positive"""
        # PositiveIntegerField raises IntegrityError, not ValueError
        with self.assertRaises(IntegrityError):
            Invoice.objects.create(
                ledger=self.ledger,
                amount_cents=-100,
                due_date=date.today(),
                status='pending'
            )

    def test_payment_amount_cents_validation(self):
        """Test Payment amount_cents must be positive"""
        # PositiveIntegerField raises IntegrityError, not ValueError
        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                invoice=self.invoice,
                amount_cents=-100,
                payment_method='card',
                paid_at=timezone.now()
            )

class FinanceSerializerTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create dependencies
        self.department = Department.objects.create(name='Test Dept')
        self.program = Program.objects.create(name='Test Program', department=self.department)
        # Create test users
        self.admin_user = User.objects.create_user(
            login_id='admin',
            password='adminpass123',
            is_staff=True
        )
        self.student_user = User.objects.create_user(
            login_id='teststudent',
            password='testpass123',
            is_staff=False
        )
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='STU001',
            program=self.program
        )
        self.ledger = Ledger.objects.create(
            student=self.student,
            balance_cents=50000
        )
        self.invoice = Invoice.objects.create(
            ledger=self.ledger,
            amount_cents=10000,
            description='Tuition Fee',
            due_date=date.today() + timedelta(days=30),
            status='pending'
        )
        self.payment = Payment.objects.create(
            invoice=self.invoice,
            amount_cents=5000,
            payment_method='card',
            paid_at=timezone.now()
        )

    def test_ledger_serializer(self):
        """Test LedgerSerializer serialization and deserialization"""
        serializer = LedgerSerializer(self.ledger)
        data = serializer.data
        self.assertEqual(data['student'], str(self.student))
        self.assertEqual(data['balance_cents'], 50000)
        self.assertTrue(data['created_at'])
        self.assertTrue(data['updated_at'])

        # Test creation
        new_data = {
            'student_id': self.student.id,
            'balance_cents': 100000
        }
        serializer = LedgerSerializer(data=new_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        new_ledger = serializer.save()
        self.assertEqual(new_ledger.student, self.student)
        self.assertEqual(new_ledger.balance_cents, 100000)

    def test_invoice_serializer(self):
        """Test InvoiceSerializer serialization and deserialization"""
        serializer = InvoiceSerializer(self.invoice)
        data = serializer.data
        self.assertEqual(data['ledger']['id'], self.ledger.id)
        self.assertEqual(data['amount_cents'], 10000)
        self.assertEqual(data['description'], 'Tuition Fee')
        self.assertEqual(data['status'], 'pending')

        # Test creation
        new_data = {
            'ledger_id': self.ledger.id,
            'amount_cents': 20000,
            'description': 'Lab Fee',
            'due_date': (date.today() + timedelta(days=15)).isoformat(),
            'status': 'pending'
        }
        serializer = InvoiceSerializer(data=new_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        new_invoice = serializer.save()
        self.assertEqual(new_invoice.ledger, self.ledger)
        self.assertEqual(new_invoice.amount_cents, 20000)

    def test_payment_serializer(self):
        """Test PaymentSerializer serialization and deserialization"""
        serializer = PaymentSerializer(self.payment)
        data = serializer.data
        self.assertEqual(data['invoice']['id'], self.invoice.id)
        self.assertEqual(data['amount_cents'], 5000)
        self.assertEqual(data['payment_method'], 'card')

        # Test creation
        new_data = {
            'invoice_id': self.invoice.id,
            'amount_cents': 3000,
            'payment_method': 'cash',
            'paid_at': timezone.now().isoformat()
        }
        serializer = PaymentSerializer(data=new_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        new_payment = serializer.save()
        self.assertEqual(new_payment.invoice, self.invoice)
        self.assertEqual(new_payment.amount_cents, 3000)

    def test_ledger_serializer_invalid_data(self):
        """Test LedgerSerializer with invalid data"""
        data = {
            'student_id': 999,  # Non-existent student
            'balance_cents': 100000
        }
        serializer = LedgerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('student_id', serializer.errors)

    def test_invoice_serializer_invalid_data(self):
        """Test InvoiceSerializer with invalid data"""
        data = {
            'ledger_id': 999,  # Non-existent ledger
            'amount_cents': 100,  # Use positive value since PositiveIntegerField validation happens at DB level
            'due_date': date.today().isoformat(),
            'status': 'pending'
        }
        serializer = InvoiceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ledger_id', serializer.errors)

    def test_payment_serializer_invalid_data(self):
        """Test PaymentSerializer with invalid data"""
        data = {
            'invoice_id': 999,  # Non-existent invoice
            'amount_cents': 100,  # Use positive value since PositiveIntegerField validation happens at DB level
            'payment_method': 'invalid'
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('invoice_id', serializer.errors)
        self.assertIn('payment_method', serializer.errors)

class FinancePermissionTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create dependencies
        self.department = Department.objects.create(name='Test Dept')
        self.program = Program.objects.create(name='Test Program', department=self.department)
        # Create test users
        self.admin_user = User.objects.create_user(
            login_id='admin',
            password='adminpass123',
            is_staff=True
        )
        self.student_user = User.objects.create_user(
            login_id='teststudent',
            password='testpass123',
            is_staff=False
        )
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='STU001',
            program=self.program
        )
        self.ledger = Ledger.objects.create(student=self.student, balance_cents=50000)
        self.invoice = Invoice.objects.create(
            ledger=self.ledger,
            amount_cents=10000,
            due_date=date.today() + timedelta(days=30),
            status='pending'
        )

    def test_is_finance_admin_permission_admin(self):
        """Test IsFinanceAdmin allows staff users"""
        permission = IsFinanceAdmin()
        # Create a proper mock request object
        request = Mock()
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))

    def test_is_finance_admin_permission_non_admin(self):
        """Test IsFinanceAdmin denies non-staff users"""
        permission = IsFinanceAdmin()
        # Create a proper mock request object
        request = Mock()
        request.user = self.student_user
        self.assertFalse(permission.has_permission(request, None))

    def test_finance_endpoint_access_admin(self):
        """Test admin can access finance endpoints"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/finance/ledgers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_finance_endpoint_access_non_admin(self):
        """Test non-admin cannot access finance endpoints"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/finance/ledgers/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)