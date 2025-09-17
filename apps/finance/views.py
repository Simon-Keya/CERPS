from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Ledger, Invoice, Payment
from .serializers import LedgerSerializer, InvoiceSerializer, PaymentSerializer
from .permissions import IsFinanceAdmin

class LedgerViewSet(viewsets.ModelViewSet):
    queryset = Ledger.objects.all()
    serializer_class = LedgerSerializer
    permission_classes = [IsAuthenticated, IsFinanceAdmin]

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsFinanceAdmin]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsFinanceAdmin]