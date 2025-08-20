from rest_framework import serializers
from .models import Ledger, Invoice, Payment
from apps.academic.models import Student

class LedgerSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )

    class Meta:
        model = Ledger
        fields = ['id', 'student', 'student_id', 'balance_cents', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class InvoiceSerializer(serializers.ModelSerializer):
    ledger = LedgerSerializer(read_only=True)
    ledger_id = serializers.PrimaryKeyRelatedField(
        queryset=Ledger.objects.all(), source='ledger', write_only=True
    )

    class Meta:
        model = Invoice
        fields = ['id', 'ledger', 'ledger_id', 'amount_cents', 'description', 'due_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PaymentSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer(read_only=True)
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.all(), source='invoice', write_only=True
    )

    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'invoice_id', 'amount_cents', 'payment_method', 'paid_at', 'created_at']
        read_only_fields = ['id', 'created_at']