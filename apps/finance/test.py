from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import FeeStructure, Invoice, Payment

User = get_user_model()

class FinanceModelsTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='teststudent', password='pass1234')
        self.fee_structure = FeeStructure.objects.create(program='CS', academic_year='2025', amount=50000)
        self.invoice = Invoice.objects.create(student=self.student, due_date='2025-12-31', total_amount=50000)
        self.payment = Payment.objects.create(invoice=self.invoice, amount=25000, method='cash')

    def test_invoice_balance(self):
        self.assertEqual(self.invoice.total_amount, 50000)
        self.assertEqual(self.invoice.payments.first().amount, 25000)
