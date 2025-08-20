from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.academic.models import Student

class Ledger(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ledgers')
    balance_cents = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ledger'
        verbose_name_plural = 'Ledgers'

    def __str__(self):
        return f"Ledger for {self.student} - Balance: {self.balance_cents / 100:.2f}"

class Invoice(models.Model):
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='invoices')
    amount_cents = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return f"Invoice {self.id} - {self.ledger.student} - {self.amount_cents / 100:.2f}"

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount_cents = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
    ])
    paid_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"Payment {self.id} - {self.invoice} - {self.amount_cents / 100:.2f}"